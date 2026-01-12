"use client";

import { motion } from "framer-motion";
import { Rocket, Loader2 } from "lucide-react";

export default function Input({
    instanceId,
    setInstanceId,
    context,
    setContext,
    loading,
    onSubmit,
}) {
    return (
        <motion.div
            key="input"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center min-h-[calc(100vh-120px)] px-6"
        >
            <div className="max-w-2xl w-full">
                <div className="text-center mb-10">
                    <h2 className="text-4xl font-bold mb-3">Deploy AI Agent</h2>
                    <p className="text-zinc-500">
                        Paste a GitHub issue and let the agent fix it automatically
                    </p>
                </div>

                <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-8 backdrop-blur-sm">
                    <form onSubmit={onSubmit} className="space-y-6">
                        <div>
                            <label className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2 block">
                                Issue URL / Instance ID
                            </label>
                            <input
                                type="text"
                                value={instanceId}
                                onChange={(e) => setInstanceId(e.target.value)}
                                placeholder="django__django-11001"
                                required
                                className="w-full bg-black/50 border border-zinc-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-zinc-200 font-mono text-sm rounded px-3 py-2 outline-none transition-colors"
                            />
                        </div>

                        <div>
                            <label className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2 block">
                                Additional Context (Optional)
                            </label>
                            <p className="text-xs text-zinc-600 mb-2">
                                Issue descriptions are loaded from SWE-bench dataset. You can add extra context here if needed.
                            </p>
                            <textarea
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                placeholder="Optional: Provide additional context or specific instructions..."
                                rows={5}
                                className="w-full bg-black/50 border border-zinc-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-zinc-200 font-mono text-sm rounded px-3 py-2 outline-none transition-colors resize-none"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-md border-t border-white/20 border-b border-blue-800 transition-all active:scale-95 disabled:opacity-50"
                        >
                            <span className="flex items-center justify-center gap-2">
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Deploying...
                                    </>
                                ) : (
                                    <>
                                        <Rocket className="w-4 h-4" />
                                        Deploy Agent
                                    </>
                                )}
                            </span>
                        </button>
                    </form>
                </div>
            </div>
        </motion.div>
    );
}
