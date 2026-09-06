"""Every ErrorSet the tool can return, in one home so unions stay consistent.

Variant names are unique ACROSS sets: typani refuses to union two sets that
share a name, and importer.py unions four of these.
"""

from __future__ import annotations

from typani import ErrorSet


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_sexpr.py::test_parse_errors_are_values
class SexprError(ErrorSet):
    UnexpectedEof = "Input ended inside an unclosed form or string"
    UnexpectedToken = "A closing paren or bare token appeared where a form was expected"
    TrailingData = "Extra content after the single top-level form"
    EmptyForm = "A form with no head token: ()"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_archive.py::test_rejects_non_library_zips
# frob:waive WIRE001 reason="consumed by archive.py" follow_up="T-0003"
class ArchiveError(ErrorSet):
    NotAZip = "The file is not a readable zip archive"
    NoSymbolLibrary = "The archive contains no .kicad_sym file"
    AmbiguousSymbolLibrary = "The archive contains more than one .kicad_sym file"
    NoFootprints = "The archive contains no .kicad_mod under a .pretty directory"
    UnsafePath = "An archive member path is absolute or escapes with .."
    NotUtf8 = "An archive member is not valid UTF-8 text"
    MemberReadFailed = "An archive member could not be read"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_project.py::test_locate_errors
# frob:waive WIRE001 reason="consumed by project.py" follow_up="T-0004"
class ProjectError(ErrorSet):
    NotAProject = "No .kicad_pro found at or under the given path"
    AmbiguousProject = "More than one .kicad_pro in the directory; pass the file"
    ProjectPathMissing = "The given project path does not exist"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_libtable.py::test_malformed_table_is_an_error
# frob:waive WIRE001 reason="consumed by libtable.py" follow_up="T-0004"
class LibTableError(ErrorSet):
    TableReadFailed = "The lib table could not be read"
    TableMalformed = "The lib table did not parse as (sym_lib_table|fp_lib_table ...)"
    TableWriteFailed = "The lib table could not be written"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_symbols.py::test_malformed_inputs_are_errors
# frob:waive WIRE001 reason="consumed by symbols.py" follow_up="T-0005"
class SymbolError(ErrorSet):
    VendorMalformed = "The vendor .kicad_sym did not parse"
    LibraryMalformed = "The project .kicad_sym did not parse"
    LibraryReadFailed = "The project .kicad_sym could not be read"
    LibraryWriteFailed = "The project .kicad_sym could not be written"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_footprints.py::test_unwritable_dir_is_an_error
# frob:waive WIRE001 reason="consumed by footprints.py" follow_up="T-0005"
class FootprintError(ErrorSet):
    FootprintWriteFailed = "A .kicad_mod could not be written into the .pretty dir"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_state.py::test_malformed_state_is_an_error
# frob:waive WIRE001 reason="consumed by state.py" follow_up="T-0007"
class StateError(ErrorSet):
    StateReadFailed = "The processed-state file could not be read"
    StateMalformed = "The processed-state file is not valid JSON for this version"
    StateWriteFailed = "The processed-state file could not be written"
    HashFailed = "The zip could not be hashed"


# frob:doc docs/design/00-overview.md#error-sets-errorspy
# frob:tests tests/unit/test_app.py::test_bad_poll_is_a_config_error
# frob:waive WIRE001 reason="consumed by app/config.py" follow_up="T-0008"
class ConfigError(ErrorSet):
    NoDownloadsDir = "No Downloads directory was given and none could be detected"
    BadPoll = "Poll interval must be a positive number of seconds"
    BadConfigFile = "The config file did not parse as TOML"
