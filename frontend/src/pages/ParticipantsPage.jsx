import React from "react";
import MainLayout from "../components/layout/MainLayout";
import ParticipantsPanel from "../components/participants/ParticipantsPanel";
import useParticipants from "../hooks/useParticipants";
import { Users, UserCheck, ShieldAlert, Clock } from "lucide-react";

export default function ParticipantsPage() {
  const { participants, loading, error } = useParticipants();

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
              <Users className="text-blue-600" size={32} />
              Interview Participants
            </h1>
            <p className="text-slate-500 mt-1">
              Real-time monitoring and verification of candidate identities across active meetings.
            </p>
          </div>
        </div>

        {/* Overview Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3.5 bg-blue-50 text-blue-600 rounded-xl">
              <Users size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Total Participants</p>
              <p className="text-2xl font-bold text-slate-800">{loading ? "..." : participants.length}</p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3.5 bg-emerald-50 text-emerald-600 rounded-xl">
              <UserCheck size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Verified Candidates</p>
              <p className="text-2xl font-bold text-slate-800">
                {loading
                  ? "..."
                  : participants.filter((p) => (p.confidence ?? 0.8) >= 0.7).length}
              </p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="p-3.5 bg-amber-50 text-amber-600 rounded-xl">
              <ShieldAlert size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Flagged Sessions</p>
              <p className="text-2xl font-bold text-slate-800">
                {loading
                  ? "..."
                  : participants.filter((p) => (p.confidence ?? 0.8) < 0.7).length}
              </p>
            </div>
          </div>
        </div>

        {/* Participants Panel */}
        {loading ? (
          <div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500">
            Loading participants list...
          </div>
        ) : error ? (
          <div className="bg-white p-6 rounded-xl border border-red-200 text-red-600">
            Failed to load participants: {error.message || "Unknown error"}
          </div>
        ) : (
          <ParticipantsPanel participants={participants} />
        )}
      </div>
    </MainLayout>
  );
}
