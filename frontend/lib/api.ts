const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AgentRunRequest {
    instance_id: string;
    problem_statement: string;
}

export interface AgentRunResponse {
    run_id: string;
    status: string;
}

export interface AgentStatusResponse {
    run_id: string;
    status: string;
    message?: string;
    logs?: string[];
    current_step?: number;
}

export async function startAgentRun(
    instanceId: string,
    problemStatement: string
): Promise<AgentRunResponse> {
    const response = await fetch(`${API_BASE_URL}/api/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            instance_id: instanceId,
            problem_statement: problemStatement,
        }),
    });

    if (!response.ok) {
        throw new Error(`Failed to start agent run: ${response.statusText}`);
    }

    return response.json();
}

export async function getRunStatus(runId: string): Promise<AgentStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/status/${runId}`);

    if (!response.ok) {
        throw new Error(`Failed to get run status: ${response.statusText}`);
    }

    return response.json();
}
