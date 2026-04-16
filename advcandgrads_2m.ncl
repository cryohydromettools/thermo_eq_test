;-----------------------------------------
; t_adv_cfd_write.ncl
; Compute horizontal advection of T and its gradients
; using advect_variable_cfd on a regional grid
;-----------------------------------------
begin
   infile  = "/home/lacrio/Documents/thermo_eq_test_lev/data/era5_t_uv_2m_20200201_20200209.nc"
   outfile = "era5_T2_202002_t_adv_and_grads_2m.nc"
  ;infile  = input
  ;outfile = output

  if (.not. fileexists(infile)) then
    print("❌ File not found: " + infile)
    exit
  end if

  ; Read
  f = addfile(infile,"r")
  T = f->t2m         ; (valid_time, latitude, longitude) at 975 hPa (single level file)
  U = f->u10         ; m/s
  V = f->v10         ; m/s
  print("✅ opened file and read t,u,v")
  printVarSummary(T)
  print("")

  ; Ensure latitude increasing (South -> North) for all fields
  lat = T&latitude
  lon = T&longitude
  if (lat(0) .gt. lat(1)) then
    T = T(:,::-1,:)
    U = U(:,::-1,:)
    V = V(:,::-1,:)
    lat = T&latitude
    lon = T&longitude
  end if
  print("✅ pre-adv ok: lat = " + lat(0) + " ... " + lat(dimsizes(lat)-1))
  print("")

  ; Regional grid ⇒ cyclic = False
  cyclic   = False
  longName = "temp advection (regional, CFD)"
  unitsAdv = "K/s"
  opt_adv  = 1      ; return [advection, zonal_grad, meridional_grad] as a list

  ; Compute: adv(T) = U * dT/dx + V * dT/dy  (CFD, metric included)
  T_list = advect_variable_cfd(U, V, T, lat, lon, cyclic, longName, unitsAdv, opt_adv)

  Tadv =   -T_list[0]      ; K/s   (advection of temperature)
  copy_VarCoords(T, Tadv)

  Tgrx =   T_list[1]      ; K/m   (zonal gradient dT/dx)
  Tgry =   T_list[2]      ; K/m   (meridional gradient dT/dy)

  ; Nice attributes
  Tadv@long_name = "temp advection (CFD, regional)"
  Tadv@units     = "K/s"
  Tgrx@long_name = "dT/dx (CFD)"
  Tgrx@units     = "K/m"
  Tgry@long_name = "dT/dy (CFD)"
  Tgry@units     = "K/m"

  ; Quick sanity prints
  print("cfd: temp advection (K/s) :")
  printMinMax(Tadv(0,:,:), True)
  print("cfd: zonal gradient (K/m) :")
  printMinMax(Tgrx(0,:,:), True)
  print("cfd: meridional gradient (K/m) :")
  printMinMax(Tgry(0,:,:), True)
  print("✅ adv + grads ok")

  ; ---- Write output (NetCDF-4 supports int64 time coords)
  if (fileexists(outfile)) then
    system("/bin/rm -f " + outfile)
  end if
  setfileoption("nc","Format","netcdf4")
  fout = addfile(outfile,"c")

  fout->t_adv   = Tadv
  fout->tgradx  = Tgrx
  fout->tgrady  = Tgry

  ; Optional: set descriptive global attr
  fout@history = "Derived with advect_variable_cfd from " + infile

  ; Verify write
  if (.not. isfilevar(fout,"t_adv") .or. \
      .not. isfilevar(fout,"tgradx") .or. \
      .not. isfilevar(fout,"tgrady")) then
    print("❌ Write failed for " + outfile)
    exit
  end if

  print("✅ wrote: " + outfile)
end
