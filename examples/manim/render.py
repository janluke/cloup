from pprint import pprint

import cloup
from cloup import argument, command, option, option_group
from cloup.constraints import ErrorFmt, mutually_exclusive


@command(aliases=["r", "re"])
@argument("script_path", help="Script path.", type=cloup.Path(), required=True)
@argument("scene_names", help="Name of the scenes.", required=False, nargs=-1)
@option_group(
    "Global options",
    option(
        "-c", "--config_file",
        help="Specify the configuration file to use for render settings.",
    ),
    option(
        "--custom_folders", is_flag=True,
        help="Use the folders defined in the [custom_folders] section of the "
             "config file to define the output folder structure.",
    ),
    option(
        "--disable_caching", is_flag=True,
        help="Disable the use of the cache (still generates cache files).",
    ),
    option("--flush_cache", is_flag=True, help="Remove cached partial movie files."),
    option("--tex_template", help="Specify a custom TeX template file."),
    option(
        "-v", "--verbosity",
        type=cloup.Choice(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            case_sensitive=False,
        ),
        help="Verbosity of CLI output. Changes ffmpeg log level unless 5+.",
    ),
    option(
        "--notify_outdated_version/--silent", is_flag=True, default=None,
        help="Display warnings for outdated installation.",
    ),
)
@option_group(
    "Output options",
    option(
        "-o", "--output_file", multiple=True,
        help="Specify the filename(s) of the rendered scene(s).",
    ),
    option(
        "--write_to_movie", is_flag=True, default=None,
        help="Write to a file.",
    ),
    option(
        "--media_dir", type=cloup.Path(),
        help="Path to store rendered videos and latex.",
    ),
    option(
        "--log_dir", type=cloup.Path(), help="Path to store render logs."
    ),
    option(
        "--log_to_file", is_flag=True,
        help="Log terminal output to file.",
    ),
)
@option_group(
    "Render Options",
    option(
        "-n", "--from_animation_number",
        help="Start rendering from n_0 until n_1. If n_1 is left unspecified, "
             "renders all scenes after n_0.",
    ),
    option(
        "-a", "--write_all", is_flag=True,
        help="Render all scenes in the input file.",
    ),
    option(
        "-f", "--format", "file_format", default="mp4",
        type=cloup.Choice(["png", "gif", "mp4"], case_sensitive=False),
    ),
    option("-s", "--save_last_frame", is_flag=True),
    option(
        "-q", "--quality", default="h",
        type=cloup.Choice(["l", "m", "h", "p", "k"], case_sensitive=False),
        help="""\b
            Resolution and framerate of the render:
            l = 854x480  30FPS,   m = 1280x720 30FPS,
            h = 1920x1080 60FPS,  p = 2560x1440 60FPS,
            k = 3840x2160 60FPS
            """,
    ),
    option(
        "-r", "--resolution",
        help="Resolution in (W,H) for when 16:9 aspect ratio isn't possible.",
    ),
    option(
        "--fps", "--frame_rate", "frame_rate", type=float,
        help="Render at this frame rate.",
    ),
    mutually_exclusive.rephrased(
        error=f"{ErrorFmt.error}\n"
              f"Use --renderer, the other two options are deprecated."
    )(
        option(
            "--renderer",
            type=cloup.Choice(["cairo", "opengl", "webgl"], case_sensitive=False),
            help="Select a renderer for your Scene.",
        ),
        option(
            "--use_opengl_renderer", is_flag=True, hidden=True,
            help="(Deprecated) Use --renderer=opengl.",
        ),
        option(
            "--use_cairo_renderer", is_flag=True, hidden=True,
            help="(Deprecated) Use --renderer=cairo.",
        ),
    ),
    option(
        "--webgl_renderer_path", type=cloup.Path(),
        help="The path to the WebGL frontend.",
    ),
    option(
        "-t", "--transparent", is_flag=True,
        help="Render scenes with alpha channel."
    ),
)
@option_group(
    "Ease of access options",
    option(
        "--progress_bar", default="display",
        type=cloup.Choice(["display", "leave", "none"], case_sensitive=False),
        help="Display progress bars and/or keep them displayed.",
    ),
    option(
        "-p", "--preview", is_flag=True,
        help="Preview the Scene's animation. OpenGL does a live preview in a "
             "popup window. Cairo opens the rendered video file in the system "
             "default media player.",
    ),
    option(
        "-f", "--show_in_file_browser", is_flag=True,
        help="Show the output file in the file browser.",
    ),
    option("--jupyter", is_flag=True, help="Using jupyter notebook magic."),
)
def render(**kwargs):
    """Render some or all scenes defined in a Python script."""
    pprint(kwargs, indent=2)
