"use client";

import { motion } from "framer-motion";
import Sidebar from "./Sidebar";
import Terminal from "./Terminal";

export default function AgentView({ steps, currentStep, logs }) {
    return (
        <motion.div
            key="hud"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-7xl mx-auto px-6 py-8"
        >
            <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
                <Sidebar steps={steps} currentStep={currentStep} />
                <Terminal logs={logs} />
            </div>
        </motion.div>
    );
}
