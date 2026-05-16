export type UserIntent = {
  primaryGoal: string;
  constraints: string[];
  emotionalState?: string;
  timeline?: string;
  riskFactors: string[];
};
