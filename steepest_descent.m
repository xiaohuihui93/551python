syms a b c
x=[-2,-1.8,-1.7,-1.4,-1.1,-0.4,-0.2,0.5,0.9,1.3,1.4,1.6,1.8,2];
y=[12.1,9.28,11.63,8.32,1.97,4.52,3.18,1.25,5.37,7.03,5.32,8.62,8.68,10];
f=a*x.^2+b*x+c;
i=1;
mse=0;
while i<15
    mse=mse+abs(y(i)-f(i));
    i=i+1;
end
MSE=mse^2/17;%mean square error
Parameter0=[a,b,c];
Parameter1=[0,0,0];%initial parameters' value
tolerence=1e-5;
g=[diff(MSE,a),diff(MSE,b),diff(MSE,c)];
g0=subs(g,Parameter0,Parameter1);%gradient at initial a b c
direction=-g0;
H=hessian(MSE,Parameter0);%hessian matrix
H1=subs(H,Parameter0,Parameter1);
s=(g0*g0')/(g0*H1*g0');%step matlab????????????????
n=0;
abs_direction=norm(s*direction);%??
m=[];

while abs_direction>tolerence && n<=200
    direction=-g0;
    fval=subs(MSE,Parameter0,Parameter1);
    m=[m,fval];
    Parameter1=Parameter1+s*direction; %???????
    g0=subs(g,Parameter0,Parameter1);
    abs_direction=norm(s*direction);
    n=n+1;
    
end
optimal_roots=Parameter1; %???
optimal_value=fval;%f?v1?????
A=optimal_roots(1);
B=optimal_roots(2);
C=optimal_roots(3);
Y=A*x.^2+B*x+C;
figure(1);
plot(x,Y);
hold on
plot(x,y);
xlabel("X");
ylabel("Y");
figure(2);
plot([1:n],m);
xlabel("iteration number");
ylabel("Mean Square error");
