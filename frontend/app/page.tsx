"use client";

import { useState, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import { Code2, Search, Wrench, TestTube, Sparkles } from "lucide-react";
import { Input, AgentView, Results, StatusBar } from "@/components";

const steps = [
  { id: "init", label: "Initialize", icon: Sparkles },
  { id: "analyze", label: "Analyze", icon: Search },
  { id: "reproduce", label: "Reproduce", icon: Code2 },
  { id: "locate", label: "Locate Files", icon: Search },
  { id: "fix", label: "Generate Fix", icon: Wrench },
  { id: "verify", label: "Verify", icon: TestTube },
];

export default function Home() {
  const [view, setView] = useState("input");
  const [instanceId, setInstanceId] = useState("");
  const [context, setContext] = useState("");
  const [runId, setRunId] = useState("");
  const [status, setStatus] = useState("idle");
  const [currentStep, setCurrentStep] = useState(0);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [patch, setPatch] = useState("");

  // Poll for agent status and logs
  useEffect(() => {
    if (view !== "hud" || !runId) return;

    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await fetch(`http://localhost:8000/api/status/${runId}`);
        const data = await statusResponse.json();

        if (data.error) {
          clearInterval(pollInterval);
          setStatus("failed");
          setView("result");
          return;
        }

        // Update logs and current step
        setLogs(data.logs || []);
        setCurrentStep(data.current_step || 0);
        setStatus(data.status);
        setPatch(data.patch || "");

        // If completed or failed, show results
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(pollInterval);
          setTimeout(() => {
            setView("result");
          }, 1000);
        }
      } catch (error) {
        console.error("Error polling status:", error);
        clearInterval(pollInterval);
        setStatus("failed");
        setView("result");
      }
    }, 1500); // Poll every 1.5 seconds

    return () => clearInterval(pollInterval);
  }, [view, runId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLogs([]);
    setCurrentStep(0);
    setStatus("pending");

    try {
      // Call the backend API to start agent run
      const response = await fetch("http://localhost:8000/api/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          instance_id: instanceId,
          problem_statement: context,
        }),
      });

      const data = await response.json();

      if (data.run_id) {
        setRunId(data.run_id);
        setStatus("processing");
        setView("hud");
      } else {
        throw new Error("Failed to start agent run");
      }
    } catch (error) {
      console.error("Error starting agent:", error);
      setStatus("failed");
      alert("Failed to start agent. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setView("input");
    setInstanceId("");
    setContext("");
    setRunId("");
    setStatus("idle");
    setLogs([]);
    setCurrentStep(0);
    setPatch("");
  };

  return (
    <div className="min-h-screen text-white flex flex-col">
      <header className="glassmorphism border-b border-zinc-800/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-xl font-bold">SudoDev</h1>
        </div>
      </header>

      <div className="flex-1">
        <AnimatePresence mode="wait">
          {view === "input" && (
            <Input
              instanceId={instanceId}
              setInstanceId={setInstanceId}
              context={context}
              setContext={setContext}
              loading={loading}
              onSubmit={handleSubmit}
            />
          )}

          {view === "hud" && (
            <AgentView steps={steps} currentStep={currentStep} logs={logs} />
          )}

          {view === "result" && <Results status={status} patch={patch} onReset={reset} />}
        </AnimatePresence>
      </div>

      <StatusBar status={status} runId={runId} />
    </div>
  );
}
