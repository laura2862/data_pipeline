from __future__ import annotations

from _13_util._scope_common import ensure_scope_dirs

import _05_pipeline._11_fen_client_scope as _11_fen_client_scope
import _05_pipeline._12_fen_doc_scope as _12_fen_doc_scope
import _05_pipeline._13_im_doc_scope as _13_im_doc_scope


def run_fen_client_scope() -> None:
    _11_fen_client_scope.main()


def run_fen_doc_scope() -> None:
    _12_fen_doc_scope.main()


def run_im_doc_scope() -> None:
    _13_im_doc_scope.main()


def main() -> None:
    ensure_scope_dirs()

    run_fen_client_scope()
    run_fen_doc_scope()
    run_im_doc_scope()


def run_unit_tests() -> None:
    assert callable(run_fen_client_scope)
    assert callable(run_fen_doc_scope)
    assert callable(run_im_doc_scope)
    assert callable(main)

    print("_10_scoping unit tests passed.")


if __name__ == "__main__":
    # run_unit_tests()
    main()