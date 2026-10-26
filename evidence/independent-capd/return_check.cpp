#include "capd/capdlib.h"
#include "capd/poincare/mplib.h"
#include <iostream>
#include <iomanip>
#include <memory>
#include <chrono>
#include <stdexcept>
#include "geometry_generated.h"
using I=capd::MpInterval; using R=capd::multiPrec::MpReal;
using V=capd::MpIVector; using M=capd::MpIMatrix; using Base=capd::MpC1Rect2Set;
I dec(const char* s){R lo,hi;lo.get(s,R::RoundDown);hi.get(s,R::RoundUp);return I(lo,hi);}
I hull(const I&a,const I&b){return I(a.leftBound(),b.rightBound());}
void require(bool ok,const char*msg){if(!ok)throw std::runtime_error(msg);}
struct Stats {int moves=0,up=0,down=0; R gap=R(100),outer=R(100),cross=R(100); bool domain=true;};
struct Audit:Base{
 std::shared_ptr<Stats> audit;
 Audit(const Base&b,std::shared_ptr<Stats>a):Base(b),audit(a){}
 void check(){
  V y=getLastEnclosure(); ++audit->moves;
  if(audit->domain && audit->moves%128==0)std::cout<<"STEP moves="<<audit->moves<<" time="<<getCurrentTime()<<" z="<<y[1]<<" vz="<<y[3]<<std::endl;
  require(audit->moves<20000,"move limit"); require(getCurrentTime().rightBound()<100,"return time limit");
  if(audit->domain){
   I rp=sqrt(sqr(y[0])+sqr(y[1]-1)),rm=sqrt(sqr(y[0])+sqr(y[1]+1));
   I gap=capd::min(rp,rm)-I(1)/5,outer=64-sqr(y[0])-sqr(y[1]);
   require(gap.leftBound()>0,"tube horizon/domain gap unresolved");require(outer.leftBound()>0,"tube outer domain gap unresolved");
   audit->gap=std::min(audit->gap,gap.leftBound()); audit->outer=std::min(audit->outer,outer.leftBound());
  }
  // Additional guard for every attempted step, including CAPD's refinement steps.
  if(y[1].contains(0)){
   require(!y[3].contains(0),"tube section transversality unresolved");
   if(y[3].leftBound()>0){++audit->up;audit->cross=std::min(audit->cross,y[3].leftBound());}
   else ++audit->down;
  }
 }
 template<class Solver>void move(Solver&s){Base::move(s);check();}
 template<class Solver>void move(Solver&s,Audit&out)const{Base::move(s,out);out.audit=audit;out.check();}
};
struct Box {I q,w,uq,uw,sq,sw;};
Box box(int i){auto b=BOXES[i];return {dec(b[0]),dec(b[1]),dec(b[2])*dec(b[6]),dec(b[3])*dec(b[6]),dec(b[4])*dec(b[7]),dec(b[5])*dec(b[7])};}
Audit initial(Box b,I u,I s,std::shared_ptr<Stats>st){
 I u0=u.mid(),s0=s.mid(),du=u-u0,ds=s-s0;
 I w0=b.w+b.uw*u0+b.sw*s0,dw=b.uw*du+b.sw*ds,W=w0+dw;
 I g0=sqrt(1-sqr(w0));require((1-sqr(W)).leftBound()>0,"initial null graph undefined");
 I gp=-w0/g0,gpp=-1/((1-sqr(W))*sqrt(1-sqr(W)));
 V x(4),r(4);M C(4,4);C.clear();r.clear();
 x[0]=b.q+b.uq*u0+b.sq*s0;x[1]=0;x[2]=w0;x[3]=g0+I(1)/2*gpp*sqr(dw);
 C[0][0]=b.uq;C[0][1]=b.sq;C[2][0]=b.uw;C[2][1]=b.sw;C[3][0]=gp*b.uw;C[3][1]=gp*b.sw;r[0]=du;r[1]=ds;
 require(x[3].leftBound()>0,"initial departure not upward");
 return Audit(Base(x,C,r),st);
}
M target(Box b){M A(4,4);A.clear();I d=b.uq*b.sw-b.sq*b.uw;require(!d.contains(0),"singular target");A[0][0]=b.sw/d;A[0][2]=-b.sq/d;A[1][0]=-b.uw/d;A[1][2]=b.uq/d;A[2][1]=1;A[3][3]=1;return A;}
void setup(capd::MpITaylor& sol){sol.setAbsoluteTolerance(1e-20);sol.setRelativeTolerance(1e-20);sol.setMaxStep(dec("0.2"));}
void controls(){
 capd::MpIMap model(FIELD); V at(4);at.clear();at[0]=2;at[3]=1;V fv=model(at);I expected=-I(8)/(5*(sqrt(I(5))+2));I common;require(intersection(fv[2],expected,common),"model symmetric acceleration sign/value mismatch");require(fv[0].contains(0)&&fv[1].contains(1)&&fv[3].contains(0),"model symmetric plane mismatch");

 I a=dec("0.1");require(a.leftBound()<a.rightBound(),"decimal is not outward rounded");require((a*10).contains(1),"decimal inclusion");require(sqr(sqrt(I(2))).contains(2),"sqrt inclusion");require((I(1)/3*3).contains(1),"division inclusion");
 capd::MpIMap f("var:x,z,vx,vz;fun:0,vz,0,-z;");capd::MpITaylor sol(f,24);setup(sol);
 capd::MpICoordinateSection section(4,1);capd::MpIPoincareMap p(sol,section,capd::poincare::MinusPlus);
 V x(4);x.clear();x[0]=2;x[3]=1;auto st=std::make_shared<Stats>();st->domain=false;Audit set(Base(x),st);I t;V y=p(set,t);I period=2*acos(I(-1));
 require(subset(period,t),"known harmonic period not contained");require(y[0].contains(2)&&y[1].contains(0)&&y[2].contains(0)&&y[3].contains(1),"known harmonic return not contained");require(t.leftBound()>6&&t.rightBound()<7,"initial crossing not excluded");require(st->up>0&&st->down>0,"audit moves not intercepted");
 // Negative control: broad section tube containing tangency must be rejected.
 V bad(4);bad.clear();bool rejected=false;try{auto q=std::make_shared<Stats>();q->domain=false;Audit b(Base(bad),q);b.check();}catch(...){rejected=true;}require(rejected,"negative transversality control accepted");
 std::cout<<"CONTROL PASS period="<<t<<" moves="<<st->moves<<" up="<<st->up<<" down="<<st->down<<"\n";
}
void cell(int edge,const char* kind,int iu,int nu,int is,int ns){
 Box b=box(SOURCES[edge]),d=box(TARGETS[edge]);I lo=dec(STRIPS[edge][0]),hi=dec(STRIPS[edge][1]);I u;
 if(std::string(kind)=="L")u=lo;else if(std::string(kind)=="R")u=hi;else u=hull(lo+(hi-lo)*iu/nu,lo+(hi-lo)*(iu+1)/nu);
 I s=hull(I(-1)+I(2)*is/ns,I(-1)+I(2)*(is+1)/ns);
 auto st=std::make_shared<Stats>();Audit set=initial(b,u,s,st);
 capd::MpIMap f(FIELD);capd::MpITaylor sol(f,24);setup(sol);capd::MpICoordinateSection section(4,1);capd::MpIPoincareMap p(sol,section,capd::poincare::MinusPlus);
 V c(4);c.clear();c[0]=d.q;c[2]=d.w;I t;auto start=std::chrono::steady_clock::now();
 try{
 V y=p(set,c,target(d),t);require(t.leftBound()>0,"nonpositive return time");require(y[3].leftBound()>0,"return transversality unresolved");require(st->down>0,"downward crossing not audited");
 bool pass=std::string(kind)=="C1"?(y[1].leftBound()>-1&&y[1].rightBound()<1):std::string(kind)=="L"?y[0].rightBound()<-1:y[0].leftBound()>1;
 // This flag can certify a counterexample only when the ENTIRE nonempty cell image lies outside the required region.
 bool contrary=std::string(kind)=="C1"?(y[1].leftBound()>=1||y[1].rightBound()<=-1):std::string(kind)=="L"?y[0].leftBound()>=-1:y[0].rightBound()<=1;
 std::cout<<"CELL "<<edge<<" "<<kind<<" "<<iu<<"/"<<nu<<" "<<is<<"/"<<ns<<" "<<(pass?"PASS":contrary?"CONTRARY":"UNRESOLVED")<<" u="<<y[0]<<" s="<<y[1]<<" time="<<t<<" vz="<<y[3]<<" gap="<<st->gap<<" outer="<<st->outer<<" crossing="<<st->cross;
 }catch(const std::exception&e){std::cout<<"CELL "<<edge<<" "<<kind<<" "<<iu<<"/"<<nu<<" "<<is<<"/"<<ns<<" ERROR "<<e.what();}
 std::cout<<" moves="<<st->moves<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<std::endl;
}
int main(int argc,char**argv){R::setDefaultPrecision(160);std::cout<<std::setprecision(38);try{if(argc==2&&std::string(argv[1])=="controls")controls();else if(argc==8)cell(std::stoi(argv[1]),argv[2],std::stoi(argv[3]),std::stoi(argv[4]),std::stoi(argv[5]),std::stoi(argv[6]));else throw std::runtime_error("usage controls OR edge kind iu nu is ns reserved");}catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}}
