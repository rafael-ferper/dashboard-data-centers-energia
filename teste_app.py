"""Executa app.py de verdade com um streamlit falso.
Valida TODO grafico passado para st.altair_chart, que e onde o schema quebra."""

import sys, types, traceback
from contextlib import contextmanager

graficos = []


def _noop(*a, **k):
    return None


@contextmanager
def _ctx():
    yield


class _Col:
    """Serve como coluna, container, expander e tab."""

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


st = types.ModuleType("streamlit")
st.set_page_config = _noop
st.markdown = _noop
st.divider = _noop
st.subheader = _noop
st.caption = _noop
st.metric = _noop
st.title = _noop
st.columns = lambda spec, **k: [
    _Col() for _ in (spec if isinstance(spec, list) else range(spec))
]
st.container = lambda **k: _Col()
st.expander = lambda *a, **k: _Col()
st.tabs = lambda labels, **k: [_Col() for _ in labels]
st.cache_data = lambda f=None, **k: (f if f else (lambda g: g))


def _altair_chart(chart, **k):
    d = chart.to_dict()  # <-- aqui o schema e validado de verdade
    graficos.append(d)


st.altair_chart = _altair_chart
sys.modules["streamlit"] = st

try:
    exec(
        compile(open("app.py", encoding="utf-8").read(), "app.py", "exec"),
        {"__file__": "app.py"},
    )
except Exception:
    print("FALHOU:")
    traceback.print_exc()
    sys.exit(1)

print(f"OK - {len(graficos)} graficos construidos e validados")
assert len(graficos) == 6, f"esperava 6 graficos, obtive {len(graficos)}"
loc = [g.get("config", {}).get("locale", {}).get("number", {}) for g in graficos]
print("locale aplicado em todos:", all(l.get("thousands") == "." for l in loc))
