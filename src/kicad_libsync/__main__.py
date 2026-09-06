import argparse

from dotenv import load_dotenv

from kicad_libsync.app import App, AppConfig


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kicad-libsync")
    # TODO: add subparsers / arguments here
    return p


# frob:doc docs/index.md#public-api
def main() -> None:
    load_dotenv()
    args = _build_parser().parse_args()
    cfg = AppConfig.from_external(args)
    App(cfg)()


if __name__ == "__main__":
    main()
