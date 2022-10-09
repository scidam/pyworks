library(dplR)

#Загрузка данных
Lc=read.rwl('Lc13_15.rwl')

#детрендинг для всех серий методом Spline
Lc_detr = detrend(rwl = Lc, method = "Spline")
Lc_detr = detrend(rwl = Lc, method = "Spline", make.plot = T) #с картинками

#пакет для дентрендинга и оценки EPS, работаем в доп окне
library(detrendeR)
detrender()

#статистика
cor=interseries.cor(Lc.in1)
rwi.stats(Lc_detr, prewhiten=TRUE)
#общая корреляция между всеми хронологиями
mean(cor[, 1])


#строим обобщенную хронологию по индексам
Lc.crn <- chron(Lc_detr)

#удаляем ненужные строки по номерам (если мало образцов или низкий EPS)
Lc.crn <- Lc.crn[-c(1:8),]


#визуализация обобщенной хронологии
plot(Lc.crn, add.spline=TRUE, nyrs=10)
plot(Pe.in1)


#Climate
library(treeclim)
#загружаем файл с климатическими данными по одной точке
Clim=read.csv('clim13.csv')

#основная функция для выявления корреляции, selection - выбор месяцев для проверки связи
#можно еще применять скользящую корреляцию функцией moving = T
dc = dcc(Lc.crn, Clim, selection = -6:-11, method = "response")
dc
dc = dcc(Pe.in1, Clim, selection = -12:4, method = "response")
dc
dc = dcc(Pe.in1, Clim, selection = 5:9, method = "response")
dc

#выбор наилучших климат.параметров и месяцев
dc2= dcc(Lc.crn, Clim, selection =.sum("PDSI", 1:5)+.mean("Tmax", 4:6), method = 'correlation')
summary(dc2)
plot(dc)

#др. функции
sk <- skills(dc2)
sk
plot(sk)

dc3=dlm(Lc.crn, Clim, selection =.range("Prec", 7))
summary(dc3)
traceplot(dc2)

sc <- seascorr(Ps.crn, Clim, primary = 'PDSI', secondary = 'Tmin')
plot(sc)
