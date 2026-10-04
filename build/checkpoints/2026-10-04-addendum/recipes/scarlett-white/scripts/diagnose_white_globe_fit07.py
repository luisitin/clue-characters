import pathlib,numpy as np,json
from scipy.optimize import least_squares
r=pathlib.Path(__file__).resolve().parents[1]
for name in ['near','far']:
 d=np.load(r/'checks'/f'white_eye06_{name}_fit_diagnostic.npz');ap=d['aperture_xy'];z=d['baseline_rim_z'];d.close();center=ap.mean(0);_,B=np.linalg.eigh(np.cov((ap-center).T));u=B[:,-1]
 if u[0]<0:u=-u
 v=np.array([-u[1],u[0]]);B=np.stack([u,v],1);q=(ap-center)@B;extent=np.max(abs(q),axis=0);a0=extent*[1.3,1.9]+.001;h=np.sqrt(1-np.sum((q/a0)**2,1));fit=np.linalg.lstsq(np.c_[np.ones(len(q)),q,h],z,rcond=None)[0];plain_res=z-np.c_[np.ones(len(q)),q,h]@fit
 def eval_model(par):
  axes=par[:2];depth=par[2];offset=par[3:5];phi=par[5];rot=np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]]);p=(q-offset)@rot;r2=np.sum((p/axes)**2,1);hh=np.sqrt(np.maximum(1-r2,1e-6));D=np.c_[np.ones(len(q)),q];coef=np.linalg.lstsq(D,z-depth*hh,rcond=None)[0];pred=D@coef+depth*hh;return pred,coef,r2
 def residual(par):
  pred,coef,r2=eval_model(par);return np.r_[(pred-z)*1000,np.maximum(r2-.9,0)*100,par[3:5]*3]
 initial=np.r_[a0,.008,0,0,0];low=np.r_[extent*[1.02,1.05],.001,-extent*.25,-.5];high=np.r_[extent*[3,4],.040,extent*.25,.5];result=least_squares(residual,initial,bounds=(low,high),max_nfev=500,ftol=1e-10,xtol=1e-10,gtol=1e-10);pred,coef,r2=eval_model(result.x);report={'eye':name,'fixed_axes_best_unconstrained_depth_m':float(fit[-1]),'fixed_axes_residual_max_m':float(abs(plain_res).max()),'optimized_axes_m':result.x[:2].tolist(),'optimized_depth_m':float(result.x[2]),'optimized_center_offset_uv_m':result.x[3:5].tolist(),'optimized_axis_rotation_rad':float(result.x[5]),'depth_plane':coef.tolist(),'rim_residual_max_m':float(abs(pred-z).max()),'rim_residual_mean_m':float(abs(pred-z).mean()),'rim_max_ellipse_radius_squared':float(r2.max()),'evaluations':result.nfev,'converged':bool(result.success),'center_xy':center.tolist(),'base_uv_basis_xy':B.tolist(),'status':'Unapproved mathematical fit to source-orbit depth; actual profile envelope and skin transition remain required.'};(r/'checks'/f'white_eye07_{name}_ellipsoid_fit.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
