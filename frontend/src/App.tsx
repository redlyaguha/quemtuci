import { Routes, Route, Navigate } from "react-router-dom";

/**
 * Каркас маршрутизации. Страницы переносятся из HTML-прототипа в рамках
 * issue [FE-01]..[FE-08]. Пока — заглушка.
 */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Placeholder title="Кампус — каркас" />} />
      {/* TODO [FE-02]: /login */}
      {/* TODO [FE-05]: /dashboard */}
      {/* TODO [FE-04]: /knowledge */}
      {/* TODO [FE-03]: /upload */}
      {/* TODO [FE-06]: /queues, /queues/:id */}
      {/* TODO [FE-07]: /profile */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function Placeholder({ title }: { title: string }) {
  return <h1 style={{ fontFamily: "system-ui", padding: 24 }}>{title}</h1>;
}
