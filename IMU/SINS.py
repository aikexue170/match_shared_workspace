#!/usr/bin/env python3
"""SINS+ZUPT — IMU已标定，代码简化版"""
import sys, os, datetime
from collections import deque
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph.opengl as gl
from imu import IMU

DBG = None
def log(m):
    t=datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    l=f"[{t}] {m}"; print(l)
    global DBG
    if DBG is None:
        DBG=open(os.path.join(os.path.dirname(__file__)or'.','sins_dbg.log'),'w')
    DBG.write(l+'\n'); DBG.flush()

def qmul(q1,q2):
    w1,x1,y1,z1=q1;w2,x2,y2,z2=q2
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2,w1*x2+x1*w2+y1*z2-z1*y2,
                     w1*y2-x1*z2+y1*w2+z1*x2,w1*z2+x1*y2-y1*x2+z1*w2])
def qconj(q): return np.array([q[0],-q[1],-q[2],-q[3]])
def qrot(q,v):
    q/=np.linalg.norm(q); return qmul(qmul(q,np.r_[0.,v]),qconj(q))[1:]
def q2euler(q):
    q/=np.linalg.norm(q); w,x,y,z=q
    return (np.degrees(np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y))),
            np.degrees(np.arcsin(np.clip(2*(w*y-z*x),-1,1))),
            np.degrees(np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))))
G=9.80665

class Win(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.p=np.zeros(3); self.v=np.zeros(3); self.last_ts=None; self._lastq=np.array([1.,0.,0.,0.])
        self.tr=deque(maxlen=300); self._gw=deque(maxlen=40); self._aw=deque(maxlen=40)
        self._ok=False; self._bc=0; self._zdbg=0
        self._ui(); self._imu(); self._tmr()
    def _ui(self):
        self.setWindowTitle("SINS+ZUPT"); self.resize(900,700)
        self.gv=gl.GLViewWidget(); self.setCentralWidget(self.gv)
        self.gv.setBackgroundColor('#1a1a2e')
        self.gv.setCameraPosition(distance=8,azimuth=30,elevation=30)
        cols=[(1,0,0,1),(0,1,0,1),(0,0.6,1,1)]
        ends=[[3,0,0],[0,3,0],[0,0,3]]
        o=np.array([[0,0,0]],dtype=float)
        for e,c in zip(ends,cols):
            self.gv.addItem(gl.GLLinePlotItem(pos=np.vstack([o,[e]]),color=c,width=4,antialias=True))
        g=gl.GLGridItem(); g.scale(.5,.5,.5); g.translate(0,0,-1.5); self.gv.addItem(g)
        mesh=gl.MeshData.sphere(20,40,.15)
        self.sp=gl.GLMeshItem(meshdata=mesh,smooth=True,color=(1,.3,.3,1),shader='shaded')
        self.gv.addItem(self.sp)
        self.tp=gl.GLLinePlotItem(pos=np.empty((0,3)),color=(.8,.8,.8,.5),width=2)
        self.gv.addItem(self.tp)
        bc=[(1,.4,.4,1),(.4,1,.4,1),(.4,.4,1,1)]; self.bl=[]
        for c in bc:
            l=gl.GLLinePlotItem(pos=np.zeros((2,3)),color=c,width=3,antialias=True)
            self.bl.append(l); self.gv.addItem(l)
        dm=gl.MeshData.sphere(12,24,.04)
        self.bd=gl.GLMeshItem(meshdata=dm,smooth=True,color=(1,1,.2,.8),shader='shaded')
        self.gv.addItem(self.bd)
        self.sb=self.statusBar()
    def _imu(self):
        self.imu=IMU(port='/dev/ttyACM0',baudrate=460800)
        self.imu.open(); log("IMU opened")
    def _tmr(self):
        self.t=QtCore.QTimer(); self.t.timeout.connect(self._tick); self.t.start(33)
    def _tick(self):
        d=self.imu.get_data()
        if not d or not all(k in d for k in ('acc_x','acc_y','acc_z','q0','q1','q2','q3')): return
        q=np.array([d['q0'],d['q1'],d['q2'],d['q3']],dtype=float)
        self._lastq=q/np.linalg.norm(q)
        a=np.array([d['acc_x'],d['acc_y'],d['acc_z']])
        if not self._ok:
            self._bc+=1; self.sb.showMessage(f"对准 {self._bc}/100"); self._ao(q)
            if self._bc>=100: self._ok=True; log("对准完成")
            return
        dt=self._dt(d)
        # SINS
        q_rot=qconj(q)/np.linalg.norm(q)
        fn=qrot(q_rot,a); an=fn.copy(); an[2]-=G
        # ZUPT
        self._aw.append(np.linalg.norm(fn))
        still=len(self._aw)>=40 and max(self._aw)-min(self._aw)<0.8
        if still: self.v*=0.
        else: self.v+=an*dt
        self.p+=self.v*dt
        np.clip(self.p,-5,5,out=self.p)
        if self._zdbg<20:
            dfb=max(self._aw)-min(self._aw) if self._aw else 0
            log(f"Still={still} dfb={dfb:.3f} v=({self.v[0]:.3f},{self.v[1]:.3f},{self.v[2]:.3f})")
            self._zdbg+=1
        self._sc(still)
    def _dt(self,d):
        if 'smp_timestamp' not in d: return .033
        ts=d['smp_timestamp']/1000.
        if self.last_ts is None: self.last_ts=ts; return .033
        dt=ts-self.last_ts; self.last_ts=ts
        return .033 if dt<=0 or dt>.1 else dt
    def _ao(self,q):
        ax=np.column_stack([qrot(q,np.eye(3)[:,i]) for i in range(3)])
        for i,l in enumerate(self.bl): l.setData(pos=np.array([[0,0,0],ax[:,i]*.6]))
        self.sp.resetTransform(); self.bd.resetTransform()
    def _sc(self,st):
        p,v=self.p,self.v; q=self._lastq
        self.sp.resetTransform(); self.sp.translate(*p)
        self.sp.setColor((.3,1,.3,1) if st else (1,.3,.3,1))
        self.tr.append(p.copy()); self.tp.setData(pos=np.array(self.tr))
        ax=np.column_stack([qrot(q,np.eye(3)[:,i]) for i in range(3)])
        for i,l in enumerate(self.bl): l.setData(pos=np.array([p,p+ax[:,i]*.6]))
        self.bd.resetTransform(); self.bd.translate(*(p+qrot(q,np.array([.12,0,0]))))
        self.sb.showMessage(f"{'静止' if st else '运动'} p({p[0]:.2f},{p[1]:.2f},{p[2]:.2f})m v{np.linalg.norm(v):.2f}m/s [R]重置")
    def keyPressEvent(self,e):
        if e.key()==QtCore.Qt.Key_R:
            self.p[:]=0; self.v[:]=0; self.tr.clear(); self.sp.resetTransform()
            self.tp.setData(pos=np.empty((0,3))); self.bd.resetTransform()
            for l in self.bl: l.setData(pos=np.zeros((2,3))); self.last_ts=None
            self._ok=False; self._bc=0; self._zdbg=0; self._gw.clear(); self._aw.clear()
            self._lastq=np.array([1.,0.,0.,0.])
            log("---重置---"); self.sb.showMessage("已重置")
        else: super().keyPressEvent(e)
    def closeEvent(self,e):
        self.imu.close()
        if DBG: DBG.close()
        e.accept()

if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv); w=Win(); w.show(); sys.exit(app.exec_())
