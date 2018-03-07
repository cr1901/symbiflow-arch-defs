project(
	'symbiflow-arch-defs',
	license : 'ISC',
	subproject_dir : 'third_party',
	version : '0.44.1',
)

# Get the source files
# ------------------------------------------------------------------------
list_files = run_command(
	find_program(join_paths('utils', 'listfiles.py')),
	'--exclude', meson.current_build_dir(),
)
assert(list_files.returncode() == 0, 'Listing files failed.\n' + list_files.stderr())

found_files = []
foreach l : list_files.stdout().strip().split('\n')
	found_files += [l.strip()]
endforeach

files_list = found_files


muxgen_cfgs = []
foreach f : files_list
	if f.endswith('/Makefile.mux')
		muxgen_cfgs += files([f])
	endif
endforeach

ntemplate_cfgs = []
foreach f : files_list
	if f.contains('/ntemplate.')
		ntemplate_cfgs += files([f])
	endif
endforeach

verilog_files = []
foreach f : files_list
	if f.endswith('.v')
		verilog_files += files([f])
	endif
endforeach

xml_files = []
foreach f : files_list
	if f.endswith('.xml')
		xml_files += files([f])
	endif
endforeach


# muxgen
# ------------------------------------------------------------------------

muxgen_cmd = find_program(join_paths('utils', 'mux_gen.py'))
foreach cfg : muxgen_cfgs
	t = custom_target(
		cfg.underscorify(),
		command : [
			muxgen_cmd,
			'--out_dir=@OUTDIR@',
			'@INPUT@',
		],
		input : cfg,
		output : ['@BASENAME@.pb_type.xml', '@BASENAME@.model.xml'],
	)

	if t.full_path().contains('/ntemplate.')
		ntemplate_cfgs += [t[0], t[1]]
	else
		xml_files += [t[0], t[1]]
	endif
endforeach

# ntemplate
# ------------------------------------------------------------------------

foreach cfg : ntemplate_cfgs
	t = custom_target(
		cfg.underscorify(),
		command : [
			find_program('utils/n.py'),
			'@INPUT@',
			'@OUTPUT@',
		],
		input : cfg,
		# FIXME: This should be s.replace('ntemplate.', '')
		output : '@BASENAME@',
	)
	if t.full_path().endswith('.v')
		verilog_files += [t]
	elif t.full_path().endswith('.xml')
		xml_files += [t]
	endif
endforeach

# verilog files
# ------------------------------------------------------------------------

# Dependency generation for Verilog files
foreach f : verilog_files
	t = custom_target(
		f.underscorify() + '_deps',
		command : [
			find_program('utils/deps_verilog.py'),
			'--output',
			'@DEPFILE@',
			'@INPUT@',
		],
		depfile : '.@BASENAME@.d',
		input : f,
	)
endforeach

# Verilog to XML conversion
v2x_cfgs = []
foreach f : files_list
	if f.endswith('/Makefile.v2x')
		v2x_cfgs += [f]
	endif
endforeach

foreach cfg : v2x_cfgs
	# FIXME: How to find the associated Verilog file!?
	t_model = custom_target(
		v2x_cfgs.underscorify() + '_model',
		command : [
			find_program('utils/vlog/vlog_to_model.py'),
			'-o',
			'@INPUT@',
			'@OUTPUT@',
		],
		output : '@BASENAME@.model.xml',
		input : [cfg],
	)
	xml_files += [t_model]

	t_pbtype = custom_target(
		v2x_cfgs.underscorify() + '_pbtype',
		command : [
			find_program('utils/vlog/vlog_to_pbtype.py'),
			'-o',
			'@OUTPUT@',
			'@INPUT@',
		],
		input : [cfg],
		output : '@BASENAME@.pb_type.xml',
	)
	xml_files += [t_pb_type]
endforeach

# xml files
# ------------------------------------------------------------------------
foreach f : xml_files
	t = custom_target(
		f.underscorify() + '_deps',
		command : [
			find_program('utils/deps_xml.py'),
			'--output',
			'@DEPFILE@',
			'@INPUT@',
		],
		depfile : '.@BASENAME@.d',
		input : f,
	)
endforeach

# XML merge files
foreach f : xml_files
	t = custom_target(
		f.underscorify() + '_merged',
		build_by_default : true,
		command : [
			find_program('xsltproc'),
			'--nomkdir',
			'--nonet',
			'--xinclude',
			'--output',
			'@OUTPUT@',
			'common/xml/xmlsort.xsl',
			'@INPUT@',
		],
		output : '@BASENAME@.merged.xml',
		input : f,
	)
endforeach

# ------------------------------------------------------------------------
