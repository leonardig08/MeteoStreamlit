from __future__ import annotations

import functools
import logging
import os
import pathlib
import sys
import time
from typing import Callable, Optional, Union, List

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, TypeAlias
else:
    from typing import ParamSpec, TypeAlias

import pandas as pd

PathLike: TypeAlias = Union[str, pathlib.Path]
P = ParamSpec("P")


def cache_to_csv(
    filepath: PathLike, refresh_time: Optional[float] = None, create_dirs: bool = True
) -> Callable[
    [Callable[P, Union[pd.DataFrame, List[pd.DataFrame]]]], Callable[P, Union[pd.DataFrame, List[pd.DataFrame]]]
]:
    def cache_decorator(func: Callable[P, Union[pd.DataFrame, List[pd.DataFrame]]]) -> Callable[
        P, Union[pd.DataFrame, List[pd.DataFrame]]
    ]:
        @functools.wraps(func)
        def retrieve_or_cache(*args: P.args, **kwargs: P.kwargs) -> Union[pd.DataFrame, List[pd.DataFrame]]:
            def is_stale(file_path: str) -> bool:
                return os.path.exists(file_path) and refresh_time is not None and (
                    os.path.getmtime(file_path) + refresh_time < time.time()
                )

            # Caso: lista di DataFrame
            if isinstance(filepath, str) and "{i}" in filepath:
                loaded = []
                all_exist = True
                i = 1
                while True:
                    file_path = filepath.format(i=i)
                    if not os.path.exists(file_path):
                        all_exist = False
                        break
                    if is_stale(file_path):
                        os.remove(file_path)
                        all_exist = False
                        break
                    i += 1
                    if not os.path.exists(filepath.format(i=i)):
                        break

                if all_exist:
                    i = 1
                    while os.path.exists(filepath.format(i=i)):
                        loaded.append(pd.read_csv(filepath.format(i=i), index_col=0))
                        i += 1
                    return loaded

                # se cache mancante o scaduta, richiama funzione
                result = func(*args, **kwargs)
                for idx, df in enumerate(result):
                    path = filepath.format(i=idx + 1)
                    if create_dirs:
                        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(path)
                return result

            # Caso singolo DataFrame
            file_path = str(filepath)
            if os.path.exists(file_path) and not is_stale(file_path):
                return pd.read_csv(file_path, index_col=0)

            # cache mancante o scaduta
            result = func(*args, **kwargs)
            if create_dirs:
                pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            result.to_csv(file_path)
            return result

        return retrieve_or_cache

    return cache_decorator
