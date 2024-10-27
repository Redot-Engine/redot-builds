#!/usr/bin/env python3

import argparse
import os


def get_version_name(version_version: str, version_status: str, version_status_version: int) -> str:
    version_name = version_version

    if version_status == "stable":
        return version_name

    version_name += " "
    if version_status.startswith("rc"):
        version_name += f"RC"
    elif version_status.startswith("beta"):
        version_name += f"beta"
    elif version_status.startswith("alpha"):
        version_name += f"alpha"
    elif version_status.startswith("dev"):
        version_name += f"dev"
    else:
        version_name += version_status

    return f"{version_name} {str(version_status_version)}"


def get_version_description(version_version: str, version_status: str, version_flavor: str) -> str:
    version_description = ""

    if version_status == "stable":
        if version_flavor == "major":
            version_description = "a major release introducing new features and considerable changes to core systems. **Major version releases contain compatibility breaking changes, both with Godot and Redot.**"
        elif version_flavor == "minor":
            version_description = "a feature release improving upon the previous version in many aspects, such as usability and performance. Feature releases also contain new features, but preserve compatibility with previous releases."
        else:
            version_description = "a lesser release mostly addressing stability and usability issues, backporting smaller feature improvements, and fixing all sorts of bugs. Minor releases are compatible with previous releases and are recommended for adoption."
    else:
        flavor_name = "lesser"
        if version_flavor == "major":
            flavor_name = "major"
        elif version_flavor == "minor":
            flavor_name = "feature"

        if version_status.startswith("rc"):
            version_description = f"a release candidate for the {version_version} {flavor_name} release. Release candidates focus on finalizing the release and fixing remaining critical bugs."
        elif version_status.startswith("beta"):
            version_description = f"a beta snapshot for the {version_version} {flavor_name} release. Beta snapshots are feature-complete and provided for public beta testing to catch as many bugs as possible ahead of the stable release."
        else: # alphas and devs go here.
            version_description = f"a dev snapshot for the {version_version} {flavor_name} release. Dev snapshots are in-development builds of the engine provided for early testing and feature evaluation while the engine is still being worked on."

    return version_description


def get_release_notes_url(version_version: str, version_status: str, version_flavor: str, version_status_version: int) -> str:
    release_notes_slug = ""
    version_sluggified = version_version.replace(".", "-")

    if version_status == "stable":
        release_notes_slug = version_sluggified
    else:
        if version_status.startswith("rc"):
            release_notes_slug = f"{version_sluggified}-rc-{version_status_version}"
        elif version_status.startswith("beta"):
            release_notes_slug = f"{version_sluggified}-beta-{version_status_version}"
        elif version_status.startswith("alpha"):
            release_notes_slug = f"{version_sluggified}-alpha-{version_status_version}"
        elif version_status.startswith("dev"):
            release_notes_slug = f"{version_sluggified}-dev-{version_status_version}"
        else:
            release_notes_slug = f"{version_sluggified}-{version_status_version}"

    return f"https://redotengine.org/news/release-{release_notes_slug}/"


def generate_notes(version_version: str, version_status: str, version_status_version: int, git_reference: str) -> None:
    notes = ""

    version_tag = f"{version_version}-{version_status}.{str(version_status_version)}"

    version_bits = version_version.split(".")
    version_flavor = "patch"
    if len(version_bits) == 2 and version_bits[1] == "0":
        version_flavor = "major"
    elif len(version_bits) == 2 and version_bits[1] != "0":
        version_flavor = "minor"

    # Add the intro line.

    version_name = get_version_name(version_version, version_status, version_status_version)
    version_description = get_version_description(version_version, version_status, version_flavor)

    notes += f"**Redot {version_name}** is {version_description}\n\n"

    # Link to the bug tracker.

    notes += "Report bugs on GitHub after checking that they haven't been reported:\n"
    notes += "- https://github.com/Redot-Engine/redot-engine/issues\n"
    notes += "\n"

    # Add build information.

    # Only for pre-releases.
    if version_status != "stable":
        commit_hash = git_reference
        notes += f"Built from commit [{commit_hash}](https://github.com/Redot-Engine/redot-engine/commit/{commit_hash}).\n"
        notes += f"To make a custom build which would also be recognized as {version_status}, you should define `GODOT_VERSION_STATUS={version_status}` in your build environment prior to compiling.\n"
        notes += "\n"

    # Add useful links.

    notes += "----\n"
    notes += "\n"

    release_notes_url = get_release_notes_url(version_version, version_status, version_flavor, version_status_version)

    notes += f"- [Release notes]({release_notes_url})\n"

    if version_status == "stable":
        notes += f"- [Curated changelog](https://github.com/Redot-Engine/redot-engine/blob/{version_tag}/CHANGELOG.md)\n"
    else:
        pass

    notes += "- Download (GitHub): Expand **Assets** below\n"

    notes += "\n"
    notes += "*All files for this release are mirrored under **Assets** below.*\n"

    return notes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", default="", help="Redot version in the major.minor.patch format (patch should be omitted for major and minor releases).")
    parser.add_argument("-f", "--flavor", default="stable", help="Release flavor, e.g. dev, alpha, beta, rc, stable (defaults to stable).")
    parser.add_argument("-s", "--status-version", type=int, default=1, help="Release flavor version, e.g. 1, 2, 3, etc. (defaults to 1).")
    parser.add_argument("-g", "--git", default="", help="Git commit hash tagged for this release.")
    args = parser.parse_args()

    if args.version == "" or args.git == "":
        print("Failed to create release notes: Redot version and git hash cannot be empty.\n")
        parser.print_help()
        exit(1)

    release_version = args.version
    release_flavor = args.flavor
    release_status_version = args.status_version
    if release_flavor == "":
        release_flavor = "stable"
    release_tag = f"{release_version}-{release_flavor}.{str(release_status_version)}"

    release_notes = generate_notes(release_version, release_flavor, release_status_version, args.git)
    release_notes_file = f"./tmp/release-notes-{release_tag}.txt"
    with open(release_notes_file, 'w') as temp_notes:
        temp_notes.write(release_notes)

    print(f"Written release notes to '{release_notes_file}'.")


if __name__ == "__main__":
    main()
