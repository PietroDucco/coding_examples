#Problem set 2
library(miscTools)
library("maxLiK")



set.seed(999)
#parameters
n<-1000
p<-0.5
max<-60
min<-18

#data gen


X_1<-runif(n,min,max)
X_2<-rbinom(n,1,p)

beta<-c(1,0.1,1)

X<-cbind(1,X_1,X_2)

fit<-X%*%beta



logit<-function(fit){ #fit<-x%*%beta
  return((exp(fit)/(1+exp(fit))))}


pi_x<-logit(fit)

y<-rbinom(n,1,logit(fit))

data<-cbind(X,pi_x,y)


prob_fun<-function(y,fit){ #prob of Yi=yi
  int<-(logit(fit)^(y))*((1-logit(fit))^(1-y))
  return(int)
}

int_2<-(pi_x^(y))*((1-pi_x)^(1-y))


ll_fun<-function(y,fit){
  return(prod(prob_fun(y,fit)))}



loglike<-function(beta)#the likelihood function for the logit model
{
  ll <- sum(-y*log(1 + exp(-(X%*%beta))) - (1-y)*log(1 + exp(X%*%beta)))
  return(ll)
}

#c
maxfun<-function(beta,X,y){
  scores_log<-matrix(NA,3,21)
  scores_ll<-matrix(NA,3,21)
 for(b in 1:length(beta)){
   seq_b<-seq(beta[b]-1,beta[b]+1,by=0.1)
   for(i in 1:length(seq_b)){
 new_beta<-beta
 new_beta[b]<-seq_b[i]
 new_fit<-X%*%new_beta
 scores_log[b,i]<-loglike(new_beta)
 scores_ll[b,i]<-ll_fun(y,new_fit)
         
 } 
 }
  return(list(scores_log,scores_ll))
}

li<-maxfun(beta,X,y)
row_max_log<-apply(li[[1]],1,max)
row_max_like<-apply(li[[2]],1,max)

#check if they are maximized at the same

for (i in 1:3){
print( (which(li[[1]][i,]==row_max_log[i],arr.ind=TRUE))==(which(li[[2]][i,]==row_max_like[i],arr.ind=TRUE)))
      }



#d
estim<-maxBFGS(loglike,finalHessian=TRUE,start=c(0,1,1))#initialize estimation procedure.


estim_par<-estim$estimate

estim_hess<-estim$hessian###the optimization routine returns the hessian matrix at the last iteration.
Cov<--(solve(estim_hess))##the covariance matrix is the (negative) inverse of the hessian matrix.
sde<-sqrt(diag(Cov))#the standard errors are the square root of the diagonal of the inverse Hessian. 
sde

#e
#interpretation intercept
intercept_startin_pred<-exp(estim_par[1])/(1+exp(estim_par[1])) #represent the starting value in absence of the other characteristics

var_pi_b1<-exp(estim_par[2])*exp(fit)/(1+exp(estim_par[2])*exp(fit)) #variation of pi due to var of 1 in X_1
var_pi_b2<-exp(estim_par[3]*exp(fit))/(1+exp(estim_par[3]*exp(fit))) #variation of pi due to var of 1 in X_2



#f
beta_intervals<-matrix(c(estim_par-2*sde, estim_par+2*sde),3,2)
y_hat<-rbinom(n,1,logit(X%*%estim_par))
y_hat_bottom<-rbinom(n,1,logit(X%*%beta_intervals[,1]))
y_hat_up<-rbinom(n,1,logit(X%*%beta_intervals[,2]))

scores<-c(sum(y_hat_bottom==y),sum(y_hat==y),sum(y==y_hat_up))/length(y)



plot(logit(X%*%estim_par))
plot(logit(X%*%beta_intervals[,1]))
plot(logit(X%*%beta_intervals[,2]))





