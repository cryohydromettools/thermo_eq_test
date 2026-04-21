;=====================================================
; Thermodynamic budget at 700 hPa (NHESS approach)
; Single ERA5 file
;=====================================================
begin

;===============================
; FILE
;===============================
infile  = infile
outfile = outfile

f = addfile(infile,"r")

;===============================
; VARIABLES
;===============================
T = f->t        ; (time, level, lat, lon)
U = f->u
V = f->v
W = f->w        ; Pa/s

lev = f->pressure_level   ; hPa
lat = f->latitude
lon = f->longitude

;===============================
; FIX LATITUDE
;===============================
if (lat(0) .gt. lat(1)) then
  T = T(:,:,::-1,:)
  U = U(:,:,::-1,:)
  V = V(:,:,::-1,:)
  W = W(:,:,::-1,:)
  lat = f->latitude(::-1)
end if

;===============================
; SELECT LEVELS
;===============================
idx700 = ind(lev.eq.700)
idx850 = ind(lev.eq.850)
idx750 = ind(lev.eq.750)

T700 = T(:,idx700,:,:)
U700 = U(:,idx700,:,:)
V700 = V(:,idx700,:,:)
W700 = W(:,idx700,:,:)

T850 = T(:,idx850,:,:)
T750 = T(:,idx750,:,:)

;===============================
; TIME (seconds)
;===============================
time = todouble(f->valid_time)
time = time - time(0)
time@units = "seconds since start"

;===============================
; dT/dt
;===============================
dT_dt = center_finite_diff_n(T700, time, False, 0, 0)
copy_VarCoords(T700, dT_dt)
dT_dt@long_name = "dT/dt at 700 hPa"
dT_dt@units = "K s-1"

;===============================
; HORIZONTAL ADVECTION
;===============================
cyclic   = False
opt_adv  = 1

T_list = advect_variable_cfd(U700, V700, T700, lat, lon, cyclic, "adv", "K/s", opt_adv)

ADV_H = T_list[0]
copy_VarCoords(T700, ADV_H)
ADV_H@long_name = "Horizontal advection"
ADV_H@units = "K s-1"

;===============================
; POTENTIAL TEMPERATURE
;===============================
kappa = 0.286

theta700 = T700 * (1000.0/700.0)^kappa
theta850 = T850 * (1000.0/850.0)^kappa
theta750 = T750 * (1000.0/750.0)^kappa

;===============================
; VERTICAL GRADIENT (850–750)
;===============================
p850 = 85000.   ; Pa
p750 = 75000.   ; Pa

dtheta_dp = (theta750 - theta850) / (p750 - p850)

;===============================
; VERTICAL ADVECTION (NHESS)
;===============================
ADV_V = - W700 * (T700/theta700) * dtheta_dp

copy_VarCoords(T700, ADV_V)
ADV_V@long_name = "Vertical advection (-omega*T/theta*dtheta/dp)"
ADV_V@units = "K s-1"

;===============================
; RESIDUAL (DIABATIC TERM)
;===============================
RES = dT_dt - ADV_H - ADV_V

copy_VarCoords(T700, RES)
RES@long_name = "Residual (diabatic heating)"
RES@units = "K s-1"

;===============================
; QUICK CHECK
;===============================
print("Check magnitudes:")
printMinMax(dT_dt, True)
printMinMax(ADV_H, True)
printMinMax(ADV_V, True)
printMinMax(RES, True)

CHECK = dT_dt - (ADV_H + ADV_V + RES)
printMinMax(CHECK, True)

;===============================
; SAVE OUTPUT
;===============================
if (fileexists(outfile)) then
  system("/bin/rm -f " + outfile)
end if

setfileoption("nc","Format","netcdf4")
fout = addfile(outfile,"c")

fout->dT_dt = dT_dt
fout->adv_h = ADV_H
fout->adv_v = ADV_V
fout->Q     = RES

fout@description = "Thermodynamic budget at 700 hPa (NHESS method)"
fout@history = "Computed from ERA5 single file"

print("✅ FILE SAVED: " + outfile)

end
