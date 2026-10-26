// Own validated Taylor/doubleton solver for the fixed R029 A-1 boxes.
// Compile without fast-math or floating contraction. Every enclosure operation
// uses binary64 with a one-ULP outward successor/predecessor.
#include <array>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <chrono>
#include <string>
#include <map>
#include <filesystem>
#include <sys/resource.h>
using namespace std;
double dn(double x){return nextafter(x,-numeric_limits<double>::infinity());}
double up(double x){return nextafter(x,numeric_limits<double>::infinity());}
struct I{
 double l,h;
 I(double x=0):l(x),h(x){}
 I(double a,double b):l(a),h(b){if(!(a<=b&&isfinite(a)&&isfinite(b)))throw runtime_error("nonfinite_interval");}
 bool zero()const{return l==0&&h==0;}
 double mid()const{return max(l,min(h,l+(h-l)*.5));}
 double mag()const{return max(abs(l),abs(h));}
 double width()const{return up(h-l);}
};
I operator+(I a,I b){if(a.zero())return b;if(b.zero())return a;return I(dn(a.l+b.l),up(a.h+b.h));}
I operator-(I a){return I(-a.h,-a.l);}
I operator-(I a,I b){return a+(-b);}
I operator*(I a,I b){if(a.zero()||b.zero())return I(0);double x[]={a.l*b.l,a.l*b.h,a.h*b.l,a.h*b.h};return I(dn(*min_element(x,x+4)),up(*max_element(x,x+4)));}
I inv(I a){if(a.l<=0&&a.h>=0)throw runtime_error("zero_denominator");return I(dn(1/a.h),up(1/a.l));}
I operator/(I a,I b){return a*inv(b);}
I root(I a){if(a.l<0)throw runtime_error("negative_sqrt");return I(a.l==0?0:dn(sqrt(a.l)),up(sqrt(a.h)));}
I hull(I a,I b){return I(min(a.l,b.l),max(a.h,b.h));}
I sym(double r){return I(-r,r);}
I square(I a){if(a.l<=0&&a.h>=0)return I(0,up(a.mag()*a.mag()));return I(dn(min(a.l*a.l,a.h*a.h)),up(max(a.l*a.l,a.h*a.h)));}
bool strict(I a,I b){return b.l<a.l&&a.h<b.h;}
I decimal(string s){bool neg=false;if(s[0]=='-'){neg=true;s=s.substr(1);}auto q=s.find('.');long long d=1;if(q!=string::npos){int n=s.size()-q-1;s.erase(q,1);for(int i=0;i<n;i++)d*=10;}long long n=stoll(s);if(neg)n=-n;if(abs(n)>9007199254740991LL||d>9007199254740991LL)throw runtime_error("decimal_not_exact_integer");return I(double(n))/I(double(d));}
struct AD{
 I v;array<I,4>d;
 AD(I x=I(0)):v(x){d.fill(I(0));}
 AD(double x):AD(I(x)){}
};
AD operator+(AD a,AD b){AD c(a.v+b.v);for(int j=0;j<4;j++)c.d[j]=a.d[j]+b.d[j];return c;}
AD operator-(AD a){AD b(-a.v);for(int j=0;j<4;j++)b.d[j]=-a.d[j];return b;}
AD operator-(AD a,AD b){return a+-b;}
AD operator*(AD a,AD b){AD c(a.v*b.v);for(int j=0;j<4;j++)c.d[j]=a.d[j]*b.v+a.v*b.d[j];return c;}
AD inv(AD a){AD b(inv(a.v));for(int j=0;j<4;j++)b.d[j]=-a.d[j]*b.v*b.v;return b;}
AD operator/(AD a,AD b){return a*inv(b);}
AD root(AD a){AD b(root(a.v));for(int j=0;j<4;j++)b.d[j]=a.d[j]/(I(2)*b.v);return b;}
template<class T>struct Jet{
 vector<T>c;
 Jet(T x,int n):c(n+1,T(0)){c[0]=x;}
 Jet(vector<T>x):c(std::move(x)){}
 int n()const{return int(c.size())-1;}
};
template<class T>Jet<T> operator+(const Jet<T>&a,const Jet<T>&b){vector<T>c(a.c);for(int i=0;i<=a.n();i++)c[i]=c[i]+b.c[i];return Jet<T>(c);}
template<class T>Jet<T> operator-(const Jet<T>&a){vector<T>c(a.c);for(auto&x:c)x=-x;return Jet<T>(c);}
template<class T>Jet<T> operator-(const Jet<T>&a,const Jet<T>&b){return a+-b;}
template<class T>Jet<T> operator*(const Jet<T>&a,const Jet<T>&b){vector<T>c(a.n()+1,T(0));for(int k=0;k<=a.n();k++)for(int j=0;j<=k;j++)c[k]=c[k]+a.c[j]*b.c[k-j];return Jet<T>(c);}
template<class T>Jet<T> inv(const Jet<T>&a){vector<T>b(a.n()+1,T(0));b[0]=inv(a.c[0]);for(int k=1;k<=a.n();k++){T s(0);for(int j=1;j<=k;j++)s=s+a.c[j]*b[k-j];b[k]=-b[0]*s;}return Jet<T>(b);}
template<class T>Jet<T> operator/(const Jet<T>&a,const Jet<T>&b){return a*inv(b);}
template<class T>Jet<T> root(const Jet<T>&a){vector<T>b(a.n()+1,T(0));b[0]=root(a.c[0]);for(int k=1;k<=a.n();k++){T s(0);for(int j=1;j<k;j++)s=s+b[j]*b[k-j];b[k]=(a.c[k]-s)/(T(2)*b[0]);}return Jet<T>(b);}
template<class T>Jet<T> operator+(const Jet<T>&a,double x){auto b=a;b.c[0]=b.c[0]+T(x);return b;}
template<class T>Jet<T> operator+(double x,const Jet<T>&a){return a+x;}
template<class T>Jet<T> operator-(const Jet<T>&a,double x){return a+(-x);}
template<class T>Jet<T> operator-(double x,const Jet<T>&a){return -a+x;}
template<class T>Jet<T> operator*(const Jet<T>&a,double x){auto b=a;for(auto&y:b.c)y=y*T(x);return b;}
template<class T>Jet<T> operator*(double x,const Jet<T>&a){return a*x;}
template<class T>Jet<T> operator/(double x,const Jet<T>&a){return x*inv(a);}
template<class T>array<T,4> rhs(const array<T,4>&y){
 auto x=y[0],z=y[1],vx=y[2],vz=y[3];
 auto rp=root(x*x+(z-1)*(z-1)),rm=root(x*x+(z+1)*(z+1));
 auto U=1+inv(rp)+inv(rm),gx=-x/(rp*rp*rp)-x/(rm*rm*rm),gz=-(z-1)/(rp*rp*rp)-(z+1)/(rm*rm*rm);
 auto dot=gx*vx+gz*vz;
 return {vx,vz,2*(gx-vx*dot)/U,2*(gz-vz*dot)/U};
}
template<class T>array<vector<T>,4> coeff(const array<T,4>&a,int n){
 array<vector<T>,4> c;for(int i=0;i<4;i++){c[i].assign(n+1,T(0));c[i][0]=a[i];}
 for(int k=0;k<n;k++){
  array<Jet<T>,4> y={Jet<T>(vector<T>(c[0].begin(),c[0].begin()+k+1)),Jet<T>(vector<T>(c[1].begin(),c[1].begin()+k+1)),Jet<T>(vector<T>(c[2].begin(),c[2].begin()+k+1)),Jet<T>(vector<T>(c[3].begin(),c[3].begin()+k+1))};
  auto f=rhs(y);for(int i=0;i<4;i++)c[i][k+1]=f[i].c[k]/T(k+1);
 }
 return c;
}
using Vec=array<I,4>;using Mat=array<array<I,4>,4>;using DM=array<array<double,4>,4>;
Mat identity(){Mat a{};for(int i=0;i<4;i++)a[i][i]=I(1);return a;}
Mat mm(const Mat&a,const Mat&b){Mat c{};for(int i=0;i<4;i++)for(int j=0;j<4;j++)for(int k=0;k<4;k++)c[i][j]=c[i][j]+a[i][k]*b[k][j];return c;}
Mat toI(const DM&a){Mat b{};for(int i=0;i<4;i++)for(int j=0;j<4;j++)b[i][j]=I(a[i][j]);return b;}
DM mid(const Mat&a){DM b{};for(int i=0;i<4;i++)for(int j=0;j<4;j++)b[i][j]=a[i][j].mid();return b;}
double norm(const Mat&a){double m=0;for(auto&row:a){I s(0);for(auto&x:row)s=s+I(x.mag());m=max(m,s.h);}return m;}
Mat jac(const Vec&x){array<AD,4>a;for(int i=0;i<4;i++){a[i]=AD(x[i]);a[i].d[i]=I(1);}auto f=rhs(a);Mat J{};for(int i=0;i<4;i++)J[i]=f[i].d;return J;}
Mat inverse(const DM&d){
 array<array<I,8>,4>a{};for(int i=0;i<4;i++)for(int j=0;j<4;j++){a[i][j]=I(d[i][j]);a[i][j+4]=I(i==j?1:0);}
 for(int k=0;k<4;k++){int p=k;for(int i=k+1;i<4;i++)if(abs(a[i][k].mid())>abs(a[p][k].mid()))p=i;swap(a[k],a[p]);I pv=a[k][k];if(pv.l<=0&&pv.h>=0)throw runtime_error("singular_basis");for(int j=0;j<8;j++)a[k][j]=a[k][j]/pv;for(int i=0;i<4;i++)if(i!=k){I v=a[i][k];for(int j=0;j<8;j++)a[i][j]=a[i][j]-v*a[k][j];}}
 Mat b{};for(int i=0;i<4;i++)for(int j=0;j<4;j++)b[i][j]=a[i][j+4];return b;
}
DM qr(const Mat&a){DM q{};for(int j=0;j<4;j++){
 array<double,4>v{};for(int i=0;i<4;i++)v[i]=a[i][j].mid();
 for(int pass=0;pass<2;pass++)for(int k=0;k<j;k++){double s=0;for(int i=0;i<4;i++)s+=q[i][k]*v[i];for(int i=0;i<4;i++)v[i]-=s*q[i][k];}
 double l=0;for(double x:v)l+=x*x;l=sqrt(l);if(!(l>1e-12))throw runtime_error("qr_failed");for(int i=0;i<4;i++)q[i][j]=v[i]/l;
 }return q;
}
struct Set{
 array<double,4>c{},r{};array<array<double,2>,4>C{};DM B{};
 Set(){for(int i=0;i<4;i++)B[i][i]=1;}
 Vec box()const{Vec x{};for(int i=0;i<4;i++){x[i]=I(c[i]);for(int j=0;j<2;j++)x[i]=x[i]+I(C[i][j])*I(-1,1);for(int j=0;j<4;j++)x[i]=x[i]+I(B[i][j])*sym(r[j]);}return x;}
 I linear(const array<I,4>&row)const{I x(0);for(int i=0;i<4;i++)x=x+row[i]*I(c[i]);for(int j=0;j<2;j++){I t(0);for(int i=0;i<4;i++)t=t+row[i]*I(C[i][j]);x=x+t*I(-1,1);}for(int j=0;j<4;j++){I t(0);for(int i=0;i<4;i++)t=t+row[i]*I(B[i][j]);x=x+t*sym(r[j]);}return x;}
};
struct Box{
 string name;array<I,2>c,u,s;array<array<I,2>,2>Ti;
 Box(string nm,const vector<string>&v):name(nm){c={decimal(v[0]),decimal(v[1])};I ru=decimal(v[6]),rs=decimal(v[7]);u={decimal(v[2])*ru,decimal(v[3])*ru};s={decimal(v[4])*rs,decimal(v[5])*rs};I det=u[0]*s[1]-u[1]*s[0];Ti={array<I,2>{s[1]/det,-s[0]/det},array<I,2>{-u[1]/det,u[0]/det}};}
 Set initial(double ul,double uh,double sl,double sh)const{
  Set a;I um=(I(ul)+I(uh))/I(2),sm=(I(sl)+I(sh))/I(2),ur=(I(uh)-I(ul))/I(2),sr=(I(sh)-I(sl))/I(2);
  I qc=c[0]+u[0]*um+s[0]*sm,wc=c[1]+u[1]*um+s[1]*sm;
  a.c[0]=qc.mid();a.c[2]=wc.mid();I vzc=root(I(1)-square(I(a.c[2])));a.c[3]=vzc.mid();
  I grad=-I(a.c[2])/vzc;array<array<I,2>,4>ci{};ci[0]={u[0]*ur,s[0]*sr};ci[2]={u[1]*ur,s[1]*sr};ci[3]={grad*ci[2][0],grad*ci[2][1]};
  for(int i=0;i<4;i++){I err(0);for(int j=0;j<2;j++){a.C[i][j]=ci[i][j].mid();err=err+I((ci[i][j]-I(a.C[i][j])).mag());}a.r[i]=err.h;}
  a.r[0]=up(a.r[0]+(qc-I(a.c[0])).mag());a.r[2]=up(a.r[2]+(wc-I(a.c[2])).mag());
  I dw=wc-I(a.c[2])+ci[2][0]*I(-1,1)+ci[2][1]*I(-1,1),wr=I(a.c[2])+dw;
  I vv=root(I(1)-square(wr));I rem=square(dw)/(I(2)*vv*vv*vv);
  I e3=vzc-I(a.c[3])+grad*(wc-I(a.c[2]));a.r[3]=up(a.r[3]+up(e3.mag()+rem.mag()));return a;
 }
};
struct Step{Set y;Vec tube;double rem=0,jrem=0,rmin=0,R2max=0;int picard=0;};
Step advance(const Set&x,double h,int N){
 Vec X=x.box();auto f=rhs(X);Vec tube;
 for(int i=0;i<4;i++){double pad=max({up(2*h*f[i].mag()),up(10*h*h),1e-13});tube[i]=X[i]+sym(pad);}
 int k=0;for(;k<10;k++){auto ft=rhs(tube);bool ok=true;Vec image;for(int i=0;i<4;i++){image[i]=X[i]+I(0,h)*ft[i];if(!strict(image[i],tube[i]))ok=false;}if(ok)break;for(int i=0;i<4;i++)if(!strict(image[i],tube[i]))tube[i]=hull(tube[i],image[i])+sym(max(1e-14,.25*tube[i].width()));}
 if(k==10)throw runtime_error("picard_failed");
 // Once existence is proved in the strict Picard box, the entire true tube
 // also lies in X+[0,h]f(box). Intersecting twice only tightens that enclosure.
 for(int pass=0;pass<2;pass++){auto ft=rhs(tube);for(int i=0;i<4;i++){I im=X[i]+I(0,h)*ft[i];tube[i]=I(max(tube[i].l,im.l),min(tube[i].h,im.h));}}
 I rp=root(square(tube[0])+square(tube[1]-I(1))),rm=root(square(tube[0])+square(tube[1]+I(1))),rad=square(tube[0])+square(tube[1]);
 if(rp.l<=.2||rm.l<=.2||rad.h>=64)throw runtime_error("D_margin_not_proved");
 auto Jf=jac(tube);I ah=I(norm(Jf))*I(h);if(ah.h>=.5)throw runtime_error("jac_tube_too_large");I e=ah/(I(1)-ah);
 Mat Vtube=identity();for(int i=0;i<4;i++)for(int j=0;j<4;j++)Vtube[i][j]=Vtube[i][j]+sym(e.h);
 array<AD,4> ax,ab;Vec center;for(int i=0;i<4;i++){ax[i]=AD(X[i]);ax[i].d[i]=I(1);ab[i]=AD(tube[i]);ab[i].d[i]=I(1);center[i]=I(x.c[i]);}
 auto ac=coeff(center,N);auto aj=coeff(ax,N);auto ar=coeff(ab,N+1);
 vector<I> hp(N+2,I(1));for(int i=1;i<=N+1;i++)hp[i]=hp[i-1]*I(h);
 Vec cen{};Mat J{},JR{};double rr=0;
 for(int i=0;i<4;i++){
  for(int n=0;n<=N;n++){cen[i]=cen[i]+ac[i][n]*hp[n];for(int j=0;j<4;j++)J[i][j]=J[i][j]+aj[i][n].d[j]*hp[n];}
  I rem=ar[i][N+1].v*hp[N+1];cen[i]=cen[i]+rem;rr=max(rr,rem.mag());
  for(int j=0;j<4;j++)for(int z=0;z<4;z++)JR[i][j]=JR[i][j]+ar[i][N+1].d[z]*Vtube[z][j]*hp[N+1];
 }
 double jr=norm(JR);if(rr>1e-13||jr>1e-11)throw runtime_error("taylor_remainder_large");
 for(int i=0;i<4;i++)for(int j=0;j<4;j++)J[i][j]=J[i][j]+JR[i][j];
 DM M=mid(J);Set y;Mat JB=mm(J,toI(x.B));y.B=qr(JB);Mat Binv=inverse(y.B);
 array<array<I,2>,4> cdiff{};Vec err{};
 for(int i=0;i<4;i++){
  y.c[i]=cen[i].mid();err[i]=cen[i]-I(y.c[i]);
  for(int a=0;a<2;a++){
   I ci(0),di(0);for(int j=0;j<4;j++){ci=ci+I(M[i][j])*I(x.C[j][a]);di=di+(J[i][j]-I(M[i][j]))*I(x.C[j][a]);}
   y.C[i][a]=ci.mid();cdiff[i][a]=ci-I(y.C[i][a])+di;
  }
 }
 Mat EB=mm(Binv,JB);
 for(int i=0;i<4;i++){
  I ei(0);for(int j=0;j<4;j++)ei=ei+Binv[i][j]*err[j];
  I radius(ei.mag());for(int a=0;a<2;a++){I ci(0);for(int j=0;j<4;j++)ci=ci+Binv[i][j]*cdiff[j][a];radius=radius+I(ci.mag());}
  for(int j=0;j<4;j++)radius=radius+I(EB[i][j].mag())*I(x.r[j]);y.r[i]=radius.h;
 }
 auto Y=y.box();for(auto a:Y)if(a.width()>.5)throw runtime_error("wrapping_width_over_half");
 return {y,tube,rr,jr,min(rp.l,rm.l),rad.h,k+1};
}
struct Result{
 bool ok=false;string why="not_run";double time=0,tlo=0,thi=0,rmin=100,R2max=0,vzmin=100,remmax=0,jremmax=0,zleft_hi=0,zright_lo=0;int steps=0,retries=0,down_windows=0;Set event_start;Vec event_tube;map<string,array<I,2>>image;
};
double elapsed(chrono::steady_clock::time_point s){return chrono::duration<double>(chrono::steady_clock::now()-s).count();}
Result integrate(const Box&source,const vector<Box>&boxes,double ul,double uh,double sl,double sh,double baseh,int N,chrono::steady_clock::time_point start,double cap){
 Result r;Set x=source.initial(ul,uh,sl,sh);int stage=0;double t=0,event_h=baseh;bool event=false;double hmin=ldexp(1.0,-18);
 try{
  while(t<60&&r.steps<20000){
   if(elapsed(start)>cap)throw runtime_error("wall_budget");
   double h=min(stage==4?event_h:baseh,60-t);Step a;bool stepped=false;
   for(int attempt=0;attempt<18;attempt++){
    try{
     a=advance(x,h,N);
     if(stage==3&&a.tube[1].h>=0&&a.tube[3].l>0&&h>max(ldexp(1.0,-14),x.box()[1].width()/a.tube[3].l)){h*=.5;r.retries++;continue;}
     stepped=true;break;
    }catch(const exception&e){if(h<=hmin)throw;h*=.5;r.retries++;}
   }
   if(!stepped)throw runtime_error("step_reduction_exhausted");
   r.rmin=min(r.rmin,a.rmin);r.R2max=max(r.R2max,a.R2max);r.remmax=max(r.remmax,a.rem);r.jremmax=max(r.jremmax,a.jrem);
   auto end=a.y.box();
   if(stage==0){if(!(a.tube[3].l>0&&end[1].l>0))throw runtime_error("initial_departure_not_proved");stage=1;}
   else if(stage==1){if(a.tube[1].l<=0&&a.tube[3].l<=0){if(a.tube[3].h>=0)throw runtime_error("unresolved_first_down_window");stage=2;r.down_windows++;}}
   if(stage==2){if(a.tube[3].h>=0)throw runtime_error("down_transversality_not_proved");if(end[1].h<0)stage=3;}
   else if(stage==3){if(a.tube[1].h>=0&&a.tube[3].h>=0){if(a.tube[3].l<=0)throw runtime_error("unresolved_up_window");auto before=x.box();if(before[1].h>=0)throw runtime_error("up_left_sign_not_proved");stage=4;event=true;event_h=h;r.event_start=x;r.event_tube=a.tube;r.tlo=t;r.zleft_hi=before[1].h;}}
   if(stage==4){
    if(a.tube[3].l<=0)throw runtime_error("up_transversality_not_proved");
    for(int i=0;i<4;i++)r.event_tube[i]=hull(r.event_tube[i],a.tube[i]);r.vzmin=min(r.vzmin,a.tube[3].l);
    if(end[1].l>0){r.thi=t+h;r.zright_lo=end[1].l;r.ok=true;r.why="validated_first_upward_return";r.steps++;t+=h;break;}
   }
   x=a.y;t+=h;r.steps++;
  }
  if(!r.ok)throw runtime_error("no_return_before_computation_limit");
  auto f=rhs(r.event_tube);I kx=f[0]/r.event_tube[3],kw=f[2]/r.event_tube[3];double k0=kx.mid(),k1=kw.mid();I z0=r.event_start.box()[1];
  for(auto&b:boxes){array<I,2>img;for(int q=0;q<2;q++){
    I a=b.Ti[q][0],c=b.Ti[q][1];array<I,4>row={a,-a*I(k0)-c*I(k1),c,I(0)};
    img[q]=r.event_start.linear(row)-a*b.c[0]-c*b.c[1]+(a*(I(k0)-kx)+c*(I(k1)-kw))*z0;
   }r.image[b.name]=img;}
 }catch(const exception&e){r.ok=false;r.why=e.what();}
 r.time=t;return r;
}
void ji(ostream&o,I x){o<<"["<<setprecision(17)<<x.l<<","<<x.h<<"]";}
void print_result(ostream&o,const string&kind,const string&src,double ul,double uh,double sl,double sh,const Result&r){
 o<<"{\"kind\":\""<<kind<<"\",\"source\":\""<<src<<"\",\"u\":["<<setprecision(17)<<ul<<","<<uh<<"],\"s\":["<<sl<<","<<sh<<"],\"return_proved\":"<<(r.ok?"true":"false")<<",\"reason\":\""<<r.why<<"\",\"last_time\":"<<r.time<<",\"steps\":"<<r.steps<<",\"step_reductions\":"<<r.retries<<",\"rmin_lower\":"<<r.rmin<<",\"R2_upper\":"<<r.R2max<<",\"center_remainder_max\":"<<r.remmax<<",\"jacobian_remainder_norm_max\":"<<r.jremmax;
 if(r.ok){o<<",\"tau\":["<<r.tlo<<","<<r.thi<<"],\"vz_lower_event\":"<<r.vzmin<<",\"z_before_upper\":"<<r.zleft_hi<<",\"z_after_lower\":"<<r.zright_lo<<",\"down_windows\":"<<r.down_windows<<",\"target_coordinates\":{";bool first=true;for(auto&[name,a]:r.image){if(!first)o<<",";first=false;o<<"\""<<name<<"\":{\"U\":";ji(o,a[0]);o<<",\"S\":";ji(o,a[1]);o<<"}";}o<<"}";}
 o<<"}\n";o.flush();
}
int main(int argc,char**argv){
 if(argc<5){cerr<<"solver boxes.dat mode output.jsonl seconds [base_h]\n";return 2;}
 auto started=chrono::steady_clock::now();double cap=stod(argv[4]),h=argc>5?stod(argv[5]):.0625;int N=10;
 ifstream in(argv[1]);vector<Box>b;string name;while(in>>name){vector<string>v(8);for(auto&x:v)in>>x;b.emplace_back(name,v);}if(b.size()!=3)return 3;
 ofstream out(argv[3]);string mode=argv[2];int n=0,fail=0;
 try{
  if(mode=="pilot"){
   for(auto&box:b){auto r=integrate(box,b,0,0,0,0,h,N,started,cap);print_result(out,"point",box.name,0,0,0,0,r);n++;if(!r.ok)fail++;if(elapsed(started)>cap)break;}
   if(elapsed(started)<cap){auto r=integrate(b[0],b,-1,1,-1,1,h,N,started,cap);print_result(out,"whole_box",b[0].name,-1,1,-1,1,r);n++;if(!r.ok)fail++;}
  }else if(mode=="sample"){
   for(auto&box:b)for(double w:{.5,.125,.03125}){
    auto r=integrate(box,b,-w,w,-w,w,h,N,started,cap);print_result(out,"sample_cell",box.name,-w,w,-w,w,r);n++;if(!r.ok)fail++;if(elapsed(started)>cap)throw runtime_error("wall_budget");
   }
  }else if(mode=="sample2"){
   for(auto&box:b)for(auto widths:vector<pair<double,double>>{{.03125,.125},{.0078125,.03125},{.0078125,.0078125}}){
    double u=widths.first,s=widths.second;auto r=integrate(box,b,-u,u,-s,s,h,N,started,cap);print_result(out,"anisotropic_sample",box.name,-u,u,-s,s,r);n++;if(!r.ok)fail++;if(elapsed(started)>cap)throw runtime_error("wall_budget");
   }
  }else if(mode=="locate"){
   vector<pair<int,string>>edges={{0,"O"},{0,"A"},{1,"B"},{2,"O"},{2,"A"}};
   for(auto [i,target]:edges){
    double lo=-1,hi=1;auto left=integrate(b[i],b,lo,lo,0,0,h,N,started,cap);auto right=integrate(b[i],b,hi,hi,0,0,h,N,started,cap);
    print_result(out,"root_search_point",b[i].name,lo,lo,0,0,left);print_result(out,"root_search_point",b[i].name,hi,hi,0,0,right);n+=2;
    if(!(left.ok&&right.ok&&left.image[target][0].h<0&&right.image[target][0].l>0))throw runtime_error("root_bracket_not_proved");
    for(int iter=0;iter<12;iter++){
     double mid=(lo+hi)*.5;auto rr=integrate(b[i],b,mid,mid,0,0,h,N,started,cap);print_result(out,"root_search_point",b[i].name,mid,mid,0,0,rr);n++;if(!rr.ok)throw runtime_error("root_search_return_unproved");
     I U=rr.image[target][0];if(U.h<0)lo=mid;else if(U.l>0)hi=mid;else{lo=mid-1.0/512;hi=mid+1.0/512;break;}
    }
    double center=round(((lo+hi)*.5)*512)/512,half=1.0/16;
    if(center-half<=-1||center+half>=1)throw runtime_error("strip_outside_box");
    out<<"{\"selected_strip\":true,\"source\":\""<<b[i].name<<"\",\"target\":\""<<target<<"\",\"u\":["<<setprecision(17)<<center-half<<","<<center+half<<"],\"s\":[-1,1],\"method\":\"own validated point bisection; center on 1/512 grid; halfwidth 1/16; full-strip C1/C2 still unproved\"}\n";out.flush();
   }
  }else if(mode=="cover"){
   struct Band{int src;string target;double lo,hi;};vector<Band> bands;
   ifstream si(filesystem::path(argv[1]).parent_path()/"strips.dat");string src,target;double lo,hi;
   while(si>>src>>target>>lo>>hi){int bi=-1;for(int i=0;i<3;i++)if(b[i].name==src)bi=i;if(bi<0||!(lo<hi&&lo>-1&&hi<1))throw runtime_error("bad_band");bands.push_back({bi,target,lo,hi});}
   if(bands.size()!=5)throw runtime_error("need_five_bands");
   vector<pair<int,string>>tasks;for(int e=0;e<5;e++){tasks.push_back({e,"C2L"});tasks.push_back({e,"C2R"});}
   for(int e:{0,1,3,4,2})tasks.push_back({e,"C1"});
   struct Cell{string path;double ul,uh,sl,sh;};
   for(auto [edge,kind]:tasks){
    auto band=bands[edge];bool c1=kind=="C1";double u0=kind=="C2R"?band.hi:band.lo,u1=c1?band.hi:u0;
    vector<Cell>pending={{"",u0,u1,-1,1}};int leaves=0,unresolved=0,tested=0;double taskstart=elapsed(started);
    double taskcap=band.src==1?(c1?1050:100):(c1?90:40);
    out<<"{\"task_start\":true,\"edge\":"<<edge<<",\"source\":\""<<b[band.src].name<<"\",\"target\":\""<<band.target<<"\",\"condition\":\""<<kind<<"\",\"u\":["<<setprecision(17)<<u0<<","<<u1<<"],\"s\":[-1,1],\"task_cap_seconds\":"<<taskcap<<"}\n";
    while(!pending.empty()){
     Cell c=pending.back();pending.pop_back();
     if(elapsed(started)>cap-1||elapsed(started)-taskstart>taskcap){pending.push_back(c);break;}
     double uw=c.uh-c.ul,sw=c.sh-c.sl,ratio=band.src==1?1:4;
     double preU=.03125,preS=band.src==1?.03125:.125;
     bool pre=(c1&&uw>preU)||sw>preS;string action,axis,reason;Result r;bool pass=false;
     if(!pre){
      r=integrate(b[band.src],b,c.ul,c.uh,c.sl,c.sh,h,N,started,min(cap-1,taskstart+taskcap));n++;tested++;
      if(r.ok){auto img=r.image[band.target];pass=c1?(img[1].l>-1&&img[1].h<1):(kind=="C2L"?img[0].h<-1:img[0].l>1);}
      ostringstream cert;print_result(cert,"coverage_cell",b[band.src].name,c.ul,c.uh,c.sl,c.sh,r);string cr=cert.str();cr.erase(cr.size()-2);
      out<<cr<<",\"edge\":"<<edge<<",\"target\":\""<<band.target<<"\",\"condition\":\""<<kind<<"\",\"path\":\""<<c.path<<"\",\"condition_proved\":"<<(pass?"true":"false")<<"}\n";out.flush();
     }
     if(pass){action="leaf";leaves++;}
     else if(c.path.size()>=22||(!pre&&r.why=="wall_budget")){action="unresolved";unresolved++;fail++;}
     else{
      action="split";axis=(!c1||sw>ratio*uw)?"s":"u";
      if(axis=="s"){double m=(c.sl+c.sh)*.5;pending.push_back({c.path+"1",c.ul,c.uh,m,c.sh});pending.push_back({c.path+"0",c.ul,c.uh,c.sl,m});}
      else{double m=(c.ul+c.uh)*.5;pending.push_back({c.path+"1",m,c.uh,c.sl,c.sh});pending.push_back({c.path+"0",c.ul,m,c.sl,c.sh});}
     }
     out<<"{\"coverage_node\":true,\"edge\":"<<edge<<",\"condition\":\""<<kind<<"\",\"path\":\""<<c.path<<"\",\"u\":["<<c.ul<<","<<c.uh<<"],\"s\":["<<c.sl<<","<<c.sh<<"],\"action\":\""<<action<<"\",\"axis\":\""<<axis<<"\",\"pre_partition\":"<<(pre?"true":"false")<<"}\n";out.flush();
    }
    for(auto&c:pending)out<<"{\"coverage_node\":true,\"edge\":"<<edge<<",\"condition\":\""<<kind<<"\",\"path\":\""<<c.path<<"\",\"u\":["<<c.ul<<","<<c.uh<<"],\"s\":["<<c.sl<<","<<c.sh<<"],\"action\":\"pending_budget\",\"axis\":\"\"}\n";
    bool complete=pending.empty()&&unresolved==0;
    out<<"{\"task_summary\":true,\"edge\":"<<edge<<",\"condition\":\""<<kind<<"\",\"complete\":"<<(complete?"true":"false")<<",\"leaves\":"<<leaves<<",\"unresolved\":"<<unresolved<<",\"pending\":"<<pending.size()<<",\"tested\":"<<tested<<",\"wall_seconds\":"<<elapsed(started)-taskstart<<"}\n";out.flush();if(!complete)fail++;
   }
  }else if(mode=="controls"){
   vector<pair<string,I>>ar={{"one_third",I(1)/I(3)},{"minus_seven_fifths",I(-7)/I(5)}};
   I a=I(1)/I(3),c=I(-7)/I(5);
   for(auto [op,val]:vector<pair<string,I>>{{"add",a+c},{"subtract",a-c},{"multiply",a*c},{"divide",a/c},{"sqrt2",root(I(2))},{"sqrt_interval",root(I(.25,4))}}){out<<"{\"control\":\""<<op<<"\",\"result\":";ji(out,val);out<<"}\n";}
   array<AD,4>z;for(int i=0;i<4;i++){z[i]=AD(0);z[i].d[i]=I(1);}auto jets=coeff(z,10);
   for(int k=0;k<=10;k++){out<<"{\"control\":\"equilibrium_variational_taylor\",\"k\":"<<k<<",\"coefficients\":[";for(int i=0;i<4;i++){if(i)out<<",";out<<"[";for(int j=0;j<4;j++){if(j)out<<",";ji(out,jets[i][k].d[j]);}out<<"]";}out<<"]}\n";}
   Set zset;auto eq=advance(zset,1.0/256,N);out<<"{\"control\":\"exact_equilibrium_step\",\"endpoint\":[";for(int i=0;i<4;i++){if(i)out<<",";ji(out,eq.y.box()[i]);}out<<"]}\n";
   DM d{};for(int i=0;i<4;i++){d[i][i]=1;if(i<3)d[i][i+1]=.125;}
   auto di=inverse(d);out<<"{\"control\":\"inverse_upper_triangular\",\"matrix\":[";for(int i=0;i<4;i++){if(i)out<<",";out<<"[";for(int j=0;j<4;j++){if(j)out<<",";ji(out,di[i][j]);}out<<"]";}out<<"]}\n";
   for(auto&box:b){auto a=advance(box.initial(0,0,0,0),1.0/256,N);out<<"{\"control\":\"short_step_crosscheck\",\"source\":\""<<box.name<<"\",\"endpoint\":[";for(int i=0;i<4;i++){if(i)out<<",";ji(out,a.y.box()[i]);}out<<"]}\n";}
  }else throw runtime_error("unknown_mode");
 }catch(const exception&e){cerr<<e.what()<<"\n";fail++;}
 rusage ru{};getrusage(RUSAGE_SELF,&ru);
 out<<"{\"summary\":true,\"cases\":"<<n<<",\"unproved_cases\":"<<fail<<",\"wall_seconds\":"<<elapsed(started)<<",\"cpu_seconds\":"<<ru.ru_utime.tv_sec+ru.ru_utime.tv_usec*1e-6+ru.ru_stime.tv_sec+ru.ru_stime.tv_usec*1e-6<<",\"peak_rss_bytes\":"<<ru.ru_maxrss<<",\"order\":"<<N<<",\"base_h\":"<<h<<"}\n";
 return 0;
}
