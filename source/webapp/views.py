from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View

from webapp.forms import BasketOrderCreateForm, ManualOrderForm, OrderProductForm
from webapp.models import Product, Order, OrderProduct
from webapp.statistic import StatisticMixin


class IndexView(StatisticMixin, ListView):
    model = Product
    template_name = 'index.html'

    def get_queryset(self):
        return Product.objects.filter(in_order=True)


class ProductView(StatisticMixin, DetailView):
    model = Product
    template_name = 'product/detail.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')

    def get_success_url(self):
        return reverse('webapp:product_detail', kwargs={'pk': self.object.pk})


class ProductCreateView(StatisticMixin, PermissionRequiredMixin, CreateView):
    model = Product
    template_name = 'product/create.html'
    fields = ('name', 'category', 'price', 'photo')
    success_url = reverse_lazy('webapp:index')
    permission_required = 'webapp.add_product'
    permission_denied_message = "Доступ запрещён"


class BasketChangeView(StatisticMixin, View):
    def get(self, request, *args, **kwargs):
        products = request.session.get('products', [])
        pk = request.GET.get('pk')
        action = request.GET.get('action')
        next_url = request.GET.get('next', reverse('webapp:index'))
        if action == 'add':
            product = get_object_or_404(Product, pk=pk)
            if product.in_order:
                products.append(pk)
        else:
            for product_pk in products:
                if product_pk == pk:
                    products.remove(product_pk)
                    break
        request.session['products'] = products
        request.session['products_count'] = len(products)
        return redirect(next_url)


class BasketView(StatisticMixin, CreateView):
    model = Order
    form_class = BasketOrderCreateForm
    template_name = 'product/basket.html'
    success_url = reverse_lazy('webapp:index')

    def get_context_data(self, **kwargs):
        basket, basket_total = self._prepare_basket()
        kwargs['basket'] = basket
        kwargs['basket_total'] = basket_total
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self._basket_empty():
            form.add_error(None, 'В корзине отсутствуют товары!')
            return self.form_invalid(form)
        response = super().form_valid(form)
        self._save_order_products()
        self._clean_basket()
        return response

    def _prepare_basket(self):
        totals = self._get_totals()
        basket = []
        basket_total = 0
        for pk, qty in totals.items():
            product = Product.objects.get(pk=int(pk))
            total = product.price * qty
            basket_total += total
            basket.append({'product': product, 'qty': qty, 'total': total})
        return basket, basket_total

    def _get_totals(self):
        products = self.request.session.get('products', [])
        totals = {}
        for product_pk in products:
            if product_pk not in totals:
                totals[product_pk] = 0
            totals[product_pk] += 1
        return totals

    def _basket_empty(self):
        products = self.request.session.get('products', [])
        return len(products) == 0

    def _save_order_products(self):
        totals = self._get_totals()
        for pk, qty in totals.items():
            OrderProduct.objects.create(product_id=pk, order=self.object, amount=qty)

    def _clean_basket(self):
        if 'products' in self.request.session:
            self.request.session.pop('products')
        if 'products_count' in self.request.session:
            self.request.session.pop('products_count')


class Statistic(StatisticMixin, View):
    def get(self, request, *args, **kwargs):
        statistic = request.session.get('statistic')

        return render(request, 'product/statistic.html', {'statistic': statistic})


class ProductUpdateView(StatisticMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    template_name = 'product/update.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')
    context_object_name = 'product'
    permission_required = 'webapp.change_product'
    permission_denied_message = "Доступ запрещён"

    def get_success_url(self):
        return reverse('webapp:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(StatisticMixin, DeleteView):
    model = Product
    template_name = 'product/delete.html'
    success_url = reverse_lazy('webapp:index')
    context_object_name = 'product'

    def delete(self, request, *args, **kwargs):
        product = self.object = self.get_object()
        product.in_order = False
        product.save()
        return HttpResponseRedirect(self.get_success_url())


class OrderListView(LoginRequiredMixin, StatisticMixin, ListView):
    template_name = 'order/list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.has_perm('webapp.view_order'):
            return Order.objects.all().order_by('-created_at')
        return self.request.user.orders.all().order_by('-created_at')


class OrderDetailView(StatisticMixin, DetailView):
    template_name = 'order/detail.html'
    context_object_name = 'order'
    model = Order


class OrderCreateView(PermissionRequiredMixin, CreateView):
    model = Order
    form_class = ManualOrderForm
    template_name = 'order/create_order.html'
    permission_required = 'webapp.change_order'
    permission_denied_message = "Доступ запрещён"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('webapp:order', kwargs={'pk': self.object.pk})


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    model = Order
    form_class = ManualOrderForm
    template_name = 'order/update_order.html'
    permission_required = 'webapp.change_order'
    permission_denied_message = "Доступ запрещён"

    def get_success_url(self):
        return reverse('webapp:order', kwargs={'pk': self.object.pk})


class OrderDeliverView(PermissionRequiredMixin, View):
    permission_required = 'webapp.can_deliver_order'
    permission_denied_message = "Доступ запрещён"

    def get(self, request, *args, **kwargs):
        order_pk = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_pk)
        order.status = 'delivered'
        order.save()

        return redirect(reverse('webapp:order', kwargs={'pk': order_pk}))


class OrderCancelView(PermissionRequiredMixin, View):
    permission_required = 'webapp.can_cancel_order'
    permission_denied_message = "Доступ запрещён"

    def get(self, request, *args, **kwargs):
        order_pk = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_pk)
        order.status = 'canceled'
        order.save()

        return redirect(reverse('webapp:order', kwargs={'pk': order_pk}))


class OrderProductCreateView(PermissionRequiredMixin, CreateView):
    model = OrderProduct
    form_class = OrderProductForm
    template_name = 'order/add_order_product.html'
    permission_required = 'webapp.can_add_product_to_order'
    permission_denied_message = "Доступ запрещён"

    def form_valid(self, form):
        order_pk = self.kwargs.get('pk')
        self.order = Order.objects.get(pk=order_pk)
        self.object = form.save(commit=False)
        self.object.order = self.order
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('webapp:order', kwargs={'pk': self.order.pk})


class OrderProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = OrderProduct
    form_class = OrderProductForm
    template_name = 'order/update_order_product.html'
    permission_required = 'webapp.can_update_product_in_order'
    permission_denied_message = "Доступ запрещён"

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        order_product = OrderProduct.objects.get(pk=pk)
        order_pk = order_product.order.pk
        return reverse('webapp:order', kwargs={'pk': order_pk})


class OrderProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = OrderProduct
    permission_required = 'webapp.can_delete_product_from_order'
    permission_denied_message = "Доступ запрещён"

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        order_product = OrderProduct.objects.get(pk=pk)
        order_pk = order_product.order.pk
        return reverse('webapp:order', kwargs={'pk': order_pk})
