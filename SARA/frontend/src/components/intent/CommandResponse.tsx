import { CommandResponse as CommandResponseType } from "../../utils/api";

type Props = {
  data: CommandResponseType | null;
};

export default function CommandResponse({ data }: Props) {
  if (!data) return null;

  return (
    <div className="mt-6 rounded-2xl border border-gray-200 p-6 shadow-sm">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-wide text-gray-500">Intent</p>
        <p className="text-sm font-semibold">{data.intent}</p>
      </div>

      <div className="mb-4">
        <p className="text-xs uppercase tracking-wide text-gray-500">Summary</p>
        <p className="text-base text-gray-900">{data.summary}</p>
      </div>

      <div className="mb-4">
        <p className="text-xs uppercase tracking-wide text-gray-500">Priority items</p>
        {data.priority_items.length === 0 ? (
          <p className="text-sm text-gray-600">No priority items.</p>
        ) : (
          <ul className="list-disc pl-5 text-sm text-gray-800">
            {data.priority_items.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <p className="text-xs uppercase tracking-wide text-gray-500">
          Suggested next action
        </p>
        <p className="text-sm text-gray-900">{data.suggested_next_action}</p>
      </div>
    </div>
  );
}
