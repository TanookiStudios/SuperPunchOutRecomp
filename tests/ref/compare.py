import sys,glob,os
refd,ourd=sys.argv[1],sys.argv[2]
def ref(t):
    d=open(f"{refd}/{t}.ppm","rb").read(); parts=d.split(b"\n",3); w,h=map(int,parts[1].split()); return w,h,parts[3]
def ours(t):
    d=open(f"{ourd}/{t}.fb.bgrx","rb").read(); w=256; h=len(d)//(w*4)
    return w,h,bytes(x for i in range(w*h) for x in (d[i*4+2],d[i*4+1],d[i*4]))
out=[]
for f in sorted(glob.glob(refd+"/*.ppm")):
    t=os.path.basename(f)[:-4]
    if not os.path.exists(f"{ourd}/{t}.fb.bgrx"): continue
    w,h,a=ref(t); _,h2,b=ours(t); hh=min(h,h2)
    n=sum(1 for i in range(w*hh) if abs(a[i*3]-b[i*3])+abs(a[i*3+1]-b[i*3+1])+abs(a[i*3+2]-b[i*3+2])>24)
    out.append("%s:%.1f"%(t,n*100.0/(w*hh)))
print(" ".join(out))
