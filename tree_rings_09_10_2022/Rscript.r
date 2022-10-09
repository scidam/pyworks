library('dplR')
library('treeclim')
Clim=read.csv('clim13.csv')
all_files <- list.files("./data", pattern="*.rwl", full.names=TRUE)


data_list = list()
for (name in all_files) {
  df <- read.rwl(name)
  data_list <- append(data_list, list(df))
}


results=list()

for (algo in c("Spline", "ModNegExp", "Mean", "Friedman")) {
  aux_result=0
  divizor=0
  for (index in seq(1:length(data_list)))
    {
      ddl <- detrend(rwl = data_list[[index]], method = algo)  
      corr <- dcc(ddl, Clim, selection =.sum("PDSI", 1:5)+.mean("Tmax", 4:6), method = 'correlation')
      
      if (corr$coef$significant[1] == 1){
        aux_result = aux_result + corr$coef$coef[1]
        divizor = divizor + 1
      }
  }
  results = append(results, list(list(coef=aux_result/divizor, divizor=divizor)))
}




