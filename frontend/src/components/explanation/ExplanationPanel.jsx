import { FileText } from "lucide-react";

export default function ExplanationPanel({

  explanations,

  loading,

}) {

  if (loading) {

    return (

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

        <h2 className="text-xl font-semibold flex items-center gap-2">

          <FileText size={22} />

          Explainability

        </h2>

        <p className="mt-4 text-slate-500">

          Loading...

        </p>

      </div>

    );

  }

  if (!explanations || explanations.length === 0) {

    return (

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

        <h2 className="text-xl font-semibold flex items-center gap-2">

          <FileText size={22} />

          Explainability

        </h2>

        <p className="mt-4 text-slate-500">

          No explanations available.

        </p>

      </div>

    );

  }

  return (

    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

      <h2 className="text-xl font-semibold flex items-center gap-2 mb-5">

        <FileText size={22} />

        Explainability

      </h2>

      <div className="space-y-4 max-h-[420px] overflow-y-auto pr-2">

        {explanations.map((item) => (

          <div
            key={item.id}
            className="border-l-4 border-blue-500 bg-slate-50 rounded-md p-4"
          >

            <p className="font-medium text-slate-800">

              {item.evidence_type}

            </p>

            <p className="text-sm text-slate-600 mt-1">

              {item.explanation}

            </p>

            <p className="text-xs text-slate-400 mt-2">

              {new Date(
                item.created_at
              ).toLocaleString()}

            </p>

          </div>

        ))}

      </div>

    </div>

  );

}