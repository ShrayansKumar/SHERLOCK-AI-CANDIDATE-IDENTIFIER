function MeetingCard({ meeting }) {
  if (!meeting) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">
          Meeting Information
        </h2>

        <p className="text-slate-500">
          No meeting found.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">
        Meeting Information
      </h2>

      <div className="space-y-3">

        <div className="flex justify-between">
          <span className="text-slate-500">Meeting ID</span>
          <span className="font-medium">{meeting.meeting_id}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-slate-500">Platform</span>
          <span className="font-medium">{meeting.platform}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-slate-500">Candidate</span>
          <span className="font-medium">{meeting.candidate_name}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-slate-500">Interviewers</span>
          <span className="font-medium">
            {meeting.interviewer_names}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-slate-500">Status</span>

          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">
            {meeting.status}
          </span>
        </div>

      </div>
    </div>
  );
}

export default MeetingCard;