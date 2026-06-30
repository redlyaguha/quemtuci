import { useEffect, useState } from "react";

type State<T> = {
  data: T;
  loading: boolean;
  /** true, если данные взяты из фолбэка (backend недоступен/не реализован). */
  isFallback: boolean;
};

/**
 * Загрузка данных из API с фолбэком на демо-данные.
 * Пока backend-эндпоинты не реализованы, экраны остаются наполненными
 * демо-контентом из src/data/mock. Когда API готов — отдаёт реальные данные.
 */
export function useApiData<T>(fetcher: () => Promise<T>, fallback: T): State<T> {
  const [state, setState] = useState<State<T>>({
    data: fallback,
    loading: true,
    isFallback: false,
  });

  useEffect(() => {
    let alive = true;
    fetcher()
      .then((data) => {
        if (alive) setState({ data, loading: false, isFallback: false });
      })
      .catch(() => {
        if (alive) setState({ data: fallback, loading: false, isFallback: true });
      });
    return () => {
      alive = false;
    };
    // fetcher/fallback намеренно не в deps: вызывающий передаёт стабильные ссылки
    // через useCallback/модульные константы. Перезапуск — сменой key компонента.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return state;
}
