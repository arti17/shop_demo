from django.urls import path
from .views import IndexView, ProductView, ProductCreateView, BasketChangeView, BasketView, Statistic, \
    ProductUpdateView, ProductDeleteView, OrderListView, OrderDetailView, OrderDeliverView, OrderCancelView, \
    OrderCreateView, OrderUpdateView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('basket/change/', BasketChangeView.as_view(), name='basket_change'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('statistic/', Statistic.as_view(), name='statistic'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order'),
    path('order/<int:pk>/deliver/', OrderDeliverView.as_view(), name='order_deliver'),
    path('order/<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
    path('order/create_order/', OrderCreateView.as_view(), name='create_order'),
    path('order/update_order/<int:pk>', OrderUpdateView.as_view(), name='update_order'),
]
