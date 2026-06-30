import { useParams } from "react-router-dom";
import { PagePlaceholder } from "../components/PagePlaceholder";

export default function QueueDetailPage() {
  const { id } = useParams();
  return (
    <PagePlaceholder title={`Очередь #${id}`} issue="[FE-06] QueueDetailPage" />
  );
}
