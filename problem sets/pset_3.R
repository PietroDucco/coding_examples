#pset3

library("mvtnorm")
library("MASS")
library("ISLR")
#generate the distribution

n1<-300
n2<-500
sigma<-matrix(c(16,-2,-2,9),2,2)
u1<-c(-3,3)
u2<-c(5,5)

X1<-mvrnorm(n1,u1,sigma)
X2<-mvrnorm(n2,u2,sigma)

data<-rbind(cbind(1,X1),cbind(2,X2))

#a

data_gen<-function(n1,n2,u1,u2,sigma){ #generates data, Y=indicator, 1st and 2nd var
  
  
  X1<-mvrnorm(n1,u1,sigma)
  X2<-mvrnorm(n2,u2,sigma)
  
  data<-(rbind(cbind(1,X1),cbind(0,X2))) # 1 for class 1 , 0 for class 2
  df<-data.frame(data)
  colnames(df)<-c("Y","A","B")  #X_1 is the first, X_2 is the second
  return(df)
}


#b
#lda probabilities
df<-data_gen(n1,n2,u1,u2,sigma)

prob<-function(df){
  mean1<-colMeans(df[df$Y==1,])[2:3]
  mean2<-colMeans(df[df$Y==0,])[2:3]
  pi1<-dim(df[df$Y==1,])[1]/dim(df)[1]
  pi2<-dim(df[df$Y==0,])[1]/dim(df)[1]
  data<-cbind(matrix(df$A),matrix(df$B))
  #cov(data)
  #cov(df[df$Y==1,2:3])
  
  #     <- 1by2 *  2by2 *     2by1   -           1by2 * 2by2 * 2by1     + Nby1
  prob1<-data%*%(sigma^(-1))%*%mean1 -(1/2*t(mean1)%*%(sigma^-1)%*%mean1)[1,1] + log(pi1)
  
  
  prob2<-data%*%(sigma^(-1))%*%mean2 - (1/2*t(mean2)%*%(sigma^-1)%*%mean2)[1,1] + log(pi2)
  
  
  res<-data.frame(cbind(prob1,prob2))
  colnames(res)<-c("prob1","prob2")
  return(res)
}
  
pred_lda<-function(res){
  rowmax<-apply(res,1,which.max)
  return(rowmax)
}

#b


lda1<-lda(Y~A + B, data=df)
predf<-predict(lda1,df)


#do logistic

glm.fit<-glm(Y~A+B,data=df,family=binomial)
glm.probs<-predict(glm.fit,df)
glm.pred<-ifelse(glm.probs>0.5,1,0)
table(glm.pred,df$Y)

#c
test_sample<-data_gen(n1,n2,u1,u2,sigma)

mean_error<-function(df,predf){
  return(1 -sum(df$Y==predf$class)/dim(df)[1])
}
#d
mean_error_lda<-function(train_set,test_set){
  ldaf<-lda(Y~A+B,data=train_set)
  predaf<-predict(ldaf,test_set)
  error<-1 -sum(test_set$Y==predaf$class)/dim(test_set)[1]
  dati<-cbind(test_set$Y,predaf$class)
  specificity<-    sum(predaf$class[test_set$Y==1]==0)/sum(test_set$Y==1)   #negative ==1
  sensitivity<-    sum(predaf$class[test_set$Y==0]==0)/sum(test_set$Y==0)   #pos=0
  precision<-      sum(predaf$class[test_set$Y==0]==0)/sum(predaf$class==0)
  neg_pred_value<- sum(predaf$class[test_set$Y==1]==1)/sum(predaf$class==1)
  res<-data.frame(matrix(c(error,specificity,sensitivity,precision,neg_pred_value),1,5))
  colnames(res)<-c("mean_error","specificity","sensitivity","precision","neg_pred_value")
  return(res)
  }

mean_error_glm<-function(train_set,test_set){
 glm_obj<-glm(Y~A+B,data=train_set,family=binomial)
 glm.prob<-predict(glm_obj,test_set,type="response")
 glm.pred<-ifelse(glm.prob>0.5,1,0)
 error<-1 -sum(test_set$Y==glm.pred)/dim(test_set)[1]
 specificity<-    sum(glm.pred[test_set$Y==1]==0)/sum(test_set$Y==1)   #negative ==1
 sensitivity<-    sum(glm.pred[test_set$Y==0]==0)/sum(test_set$Y==0)   #pos=0
 precision<-      sum(glm.pred[test_set$Y==0]==0)/sum(glm.pred==0)
 neg_pred_value<- sum(glm.pred[test_set$Y==1]==1)/sum(glm.pred==1)
 res<-data.frame(matrix(c(error,specificity,sensitivity,precision,neg_pred_value),1,5))
 colnames(res)<-c("mean_error","specificity","sensitivity","precision","neg_pred_value")
 return(res)
}


#2a

simulation<-function(reps,n1,n2,u1,u2,sigma){
  
  errors<-matrix(NA,2,reps)
  for (i in 1:reps){
    train_set<-data_gen(n1,n2,u1,u2,sigma)
    test_set<-data_gen(n1,n2,u1,u2,sigma)
    errors[,i]<-c(mean_error_lda(train_set,test_set)$mean_error,mean_error_glm(train_set,test_set)$mean_error)
    #first lda, second glm
    
  }
  
  
  return(errors)
}
errors<-simulation(100,n1,n2,u1,u2,sigma)
means<-rowMeans(errors)

#2b
#w


#2c assigning 0 to everything is the best way to get 100% sensitivity but it makes the mean error = n1/(n1+n2)




