from datetime import datetime


class StatisticMixin:
    # Одна статистика имеет вид: {путь: [количество посещений, время в секундах, дата и время последнего посещения]}
    def dispatch(self, request, *args, **kwargs):
        statistic = request.session.get('statistic', [])            # Получение статистики
        request_path = request.path                                 # Текущий путь
        now = datetime.now()                                        # Текущие дата и время
        time_str = now.strftime('%Y-%m-%d %H:%M:%S')                # Текущие дата и время в строковом формате
        last_path = request.session.get('last_path', request_path)  # Предыдущий путь

        # Функция получения всех путей в статистике
        def get_pathes():
            pathes = []
            for stat in statistic:
                for path in stat.keys():
                    pathes.append(path)
            return pathes

        # Обновление времени проведенное на странице последнего пути
        for stat in statistic:
            for path in stat.keys():
                if path == last_path:
                    path_date = datetime.strptime(stat[last_path][2], '%Y-%m-%d %H:%M:%S')
                    diff = now - path_date
                    stat[last_path][1] += diff.seconds
                    stat[last_path][2] = time_str

        # Если путь есть в статистике, обновляем счетчик посещения и дату последнего входа на страницу
        if request_path in get_pathes():
            for stat in statistic:
                for path in stat.keys():
                    if path == request_path:
                        statistic.remove(stat)
                        stat[path][0] += 1
                        stat[path][2] = time_str
                        statistic.append(stat)
                        request.session['statistic'] = statistic
                        request.session['last_path'] = request_path
        # Если нет создаем новую статистику
        else:
            new_stat = {request_path: [1, 0, time_str]}
            statistic.append(new_stat)
            request.session['last_path'] = request_path
            request.session['statistic'] = statistic

        return super().dispatch(request, *args, **kwargs)
