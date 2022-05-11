#problem set 1

set.seed(99)
#training set
#a
beta<-c(5,-0.5);
N<-1000;
X<-cbind(1,rnorm(N*2,0,sqrt(1.5)));
eps<-rnorm(N*2,0,sqrt(10));
y<-X%*%beta + eps;

data_gen<-function(N,beta){
  
  X<-cbind(1,rnorm(N*2,0,sqrt(1.5)))
  eps<-rnorm(N*2,0,sqrt(10))
  y<-X%*%beta + eps
  return(list(X,y))
}

X_train<-X[1:N,]
X_test<-X[(N+1):(2*N),]
#b
y_train<-y[1:N,]
y_test<-y[(N+1):(2*N),]

#c
beta_estim<-solve(t(X_train)%*%X_train)%*%t(X_train)%*%y_train;

estim_beta<-function(X,y){
  return(solve(t(X)%*%X)%*%t(X)%*%y)} #compute betas
#d

X_2<-cbind(X,X[,2]^2);
X_3<-cbind(X_2,X[,2]^3);
X_4<-cbind(X_3,X[,3]^4);

Polynomial_gen<-function(X,n){ #0<=n<=4
  X_2<-cbind(X,X[,2]^2)
  X_3<-cbind(X_2,X[,2]^3)
  X_4<-cbind(X_3,X[,2]^4)
  if(n==0){
    return(matrix(X[,1]))
  }
  if(n==1){
    return(X)
  }
  if(n==2){
    return(X_2)
  } 
  if(n==3){
    return(X_3)
  }
  return(X_4)
}

test_train_split<-function(X,y){
  split<-length(y)
  
  X_train<-X[1:(split/2),]
  X_test<-X[(split/2+1):split,]
  
  y_train<-y[1:(split/2),]
  y_test<-y[(split/2+1):split,]
  
  return(list(X_train,X_test,y_train,y_test))
}


MSE<-function(beta_estim,X,y){
  y_pred<-X%*%beta_estim       #compute fitted values
  return(sum((y_pred-y)^2)/length(y))  #
  
}
#d


get_MSE_avg<-function(X,y){
  data<-test_train_split(X,y)
  beta<-estim_beta(data[[1]],data[[3]]) #data[1]=X_train, data[3]=y_train
  return(c(MSE(beta,data[[1]],data[[3]]),MSE(beta,data[[2]],data[[4]])))
}  #returns MSE and avg prediction error


#e
poly_scores<-function(N,beta){
scores<-matrix(NA,5,2)
X_y<-data_gen(N,beta)
X<-X_y[[1]]
y<-X_y[[2]]
for (i in 1:5){
  scores[i,]<-c(get_MSE_avg(Polynomial_gen(X,(i-1)),y))
  
}
return(scores)
}








#part 2

#a,b
set.seed(100)
n<-1000 #simulations
Simulation<-function(n_sim,beta,sample_size)
{
  est<-matrix(NA,n_sim,10)
  for (i in 1:n_sim){
    scores<-poly_scores(sample_size,beta)
    est[i,]<-matrix(scores,1,10) #first five are MSE, last five are pred error
    
  }
  return(est)
}



estimates<-Simulation(1000,beta,1000);
means<-colMeans(estimates);
#c
plot(0:4,means[1:5])#MSE as we can see the more variables we add the error goes down

plot(0:4,means[6:10]) #pred err,effect of number of variables and polynomials is not clear, due to overfitting
#d

# As we can see from the two plots the marginal effect of a new polynomial variable is is not big after we are at degree 1
#It does not impact the MSE much and it has a negative effect on the avg pred error



