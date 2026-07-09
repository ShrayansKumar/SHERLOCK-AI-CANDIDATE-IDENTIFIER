import ParticipantCard from "./ParticipantCard";

function ParticipantsPanel({ participants }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

      <h2 className="text-xl font-semibold text-slate-800 mb-4">
        Participants
      </h2>

      {participants.length === 0 ? (
        <p className="text-slate-500">
          No participants found.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {participants.map((participant) => (
            <ParticipantCard
              key={participant.id}
              participant={participant}
            />
          ))}
        </div>
      )}

    </div>
  );
}

export default ParticipantsPanel;