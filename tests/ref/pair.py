import sys
refd,ourd,outp=sys.argv[1:4]; tags=sys.argv[4:]
def ref(t):
    d=open(f"{refd}/{t}.ppm","rb").read(); parts=d.split(b"\n",3); w,h=map(int,parts[1].split()); return w,h,parts[3]
def ours(t):
    d=open(f"{ourd}/{t}.fb.bgrx","rb").read(); w=256; h=len(d)//(w*4)
    return w,h,bytes(x for i in range(w*h) for x in (d[i*4+2],d[i*4+1],d[i*4]))
rows=[]
for t in tags:
    w,h,a=ref(t); _,h2,b=ours(t); rows.append((a,b,w,min(h,h2)))
W=516; H=sum(r[3] for r in rows)+2*(len(rows)-1)
img=bytearray(b"\x40\x40\x40"*(W*H)); y0=0
for a,b,w,hh in rows:
    for y in range(hh):
        img[((y0+y)*W)*3:((y0+y)*W+256)*3]=b[y*w*3:(y+1)*w*3]
        img[((y0+y)*W+260)*3:((y0+y)*W+260+256)*3]=a[y*w*3:(y+1)*w*3]
    y0+=hh+2
open(outp,"wb").write(b"P6\n%d %d\n255\n"%(W,H)+bytes(img))
