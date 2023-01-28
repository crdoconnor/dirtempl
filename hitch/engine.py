from hitchstory import (
    StoryCollection,
    BaseEngine,
    exceptions,
    validate,
    no_stacktrace_for,
)
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from templex import Templex
from strictyaml import Optional, Str, Map, Int, Bool, Enum, load, MapPattern
from path import Path
import hitchpylibrarytoolkit
from hitchrunpy import (
    ExamplePythonCode,
    HitchRunPyException,
    ExpectedExceptionMessageWasDifferent,
)


CODE_TYPE = Map({"in python 2": Str(), "in python 3": Str()}) | Str()


class Engine(BaseEngine):
    """Python engine for running tests."""

    given_definition = GivenDefinition(
        image_file=GivenProperty(Str()),
        files=GivenProperty(MapPattern(Str(), Str())),
    )

    info_definition = InfoDefinition(
        status=InfoProperty(schema=Enum(["experimental", "stable"])),
        docs=InfoProperty(schema=Str()),
    )

    def __init__(self, keypath, python_path=None, rewrite=False, cprofile=False):
        self.path = keypath
        self._python_path = python_path
        self._rewrite = rewrite
        self._cprofile = cprofile

    def set_up(self):
        """Set up your applications and the test environment."""
        self.path.profile = self.path.gen.joinpath("profile")
        self.path.working = self.path.gen.joinpath("working")

        if self.path.working.exists():
            self.path.working.rmtree()
        self.path.working.mkdir()

        for filename, contents in self.given["files"].items():
            filepath = Path(filename)
            if not self.path.working.joinpath(filepath.parent).exists():
                self.path.working.joinpath(filepath.parent).makedirs()
            self.path.working.joinpath(filename).write_text(contents)
        
        if "image_file" in self.given:
            self.path.key.joinpath("example-image.png").copy(
                self.path.working.joinpath(self.given["image_file"])
            )

        if not self.path.profile.exists():
            self.path.profile.mkdir()

        self.pylibrary = hitchpylibrarytoolkit.PyLibraryBuild(
            "dirtempl", self.path
        ).with_python_version("3.7.0")
        self.pylibrary.ensure_built()
        self.python = self.pylibrary.bin.python
        self.dirtempl_bin = self.pylibrary.bin.dirtempl

    @no_stacktrace_for(AssertionError)
    @validate(cmd=Str(), output=Str(), error=Bool())
    def dirtempl(self, cmd, output, error=False):
        from shlex import split
        from templex import Templex

        command = self.dirtempl_bin(*split(cmd)).in_dir(self.path.working)

        if error:
            command = command.ignore_errors()

        actual_output = command.output()

        try:
            Templex(output).assert_match(actual_output)
        except AssertionError:
            if self._rewrite:
                self.current_step.update(output=actual_output)
            else:
                raise

    @no_stacktrace_for(FileNotFoundError)
    @no_stacktrace_for(AssertionError)
    def file_contains(self, filename, contents):
        actual_contents = self.path.working.joinpath(filename).text()
        try:
            assert contents == actual_contents
        except AssertionError:
            if self._rewrite:
                self.current_step.update(contents=actual_contents)
            else:
                raise
    
    @no_stacktrace_for(FileNotFoundError)
    def image_present(self, filename):
        assert self.path.working.joinpath(filename).read_bytes() == \
            self.path.key.joinpath("example-image.png").read_bytes()
        

    def pause(self, message="Pause"):
        import IPython

        IPython.embed()

    def on_success(self):
        if self._rewrite:
            self.new_story.save()
        if self._cprofile:
            self.python(
                self.path.key.joinpath("printstats.py"),
                self.path.profile.joinpath("{0}.dat".format(self.story.slug)),
            ).run()
