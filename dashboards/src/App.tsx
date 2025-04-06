import { PVForecastForm } from "./components/PVForecastForm";
import { Separator } from "./components/ui/separator";
import { useDebugValue, useEffect, useState } from "react";
import { PredictionTable } from "./components/PredictionTable";
import { PredictionChart } from "./components/PredicitionChart";
import OpenAI from 'openai';

function App() {
  const [predictions, setPredictions] = useState(null);
  const [openAiAnswer, setOpenAiAnswer] = useState(null);

  const client = new OpenAI({
    apiKey: import.meta.env.VITE_API_KEY, // This is the default and can be omitted
    dangerouslyAllowBrowser: true, // Use at your own risk
  });

  const bhenkalauda=async ()=>{
    const response = await client.responses.create({
      model: 'gpt-4o',
      instructions: 'You are given a timestamps with expected solar power generation in watts. Please provide a suggestions to power grid on when to lower or raise the power generation. Give the reply in strictly 2 lines highlighting only the major changes in power generation. Also suggest ways on how deal with extra power generation. *DO NOT USE MARKDOWN*',
      input: JSON.stringify(predictions),
    });

  setOpenAiAnswer(response.output_text);

  }

  useEffect(() => {
    if (predictions) {
      bhenkalauda();
    }
  }, [predictions]);


  


  // console.log("Predictions", predictions);
  return (
    <div className="flex flex-col max-w-screen-2xl max-h-screen-2xl p-10 mx-auto">
      <div className="flex items-center gap-4">
        <img
          src="solar.svg"
          alt="Logo"
          className="h-10 w-10 mr-2"
        />
      <div className="space-y-0.5">
        
        <h2 className="text-2xl font-bold tracking-tight">PV Power Forecast</h2>
        <p className="text-muted-foreground">
          Get solar energy predictions for 48 hours ahead.
        </p>
      </div>
      </div>
      <Separator className="my-6" />
      <div className="grow flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
        <aside className="lg:w-1/5">
          <PVForecastForm updatePredictions={setPredictions} />
        </aside>
        {predictions ? (
          <div className="grow flex flex-col justify-between w-2/5 p-20 gap-4">
            <PredictionChart predictions={predictions} />
            {openAiAnswer && (
              <>
        <div className="flex gap-2 flex-reverse items-center">
              <img
                src="sparkle.png"
                alt="Logo"
                className="h-10 w-10"
              />
              <h1 className="text-xl font-bold">Suggestions</h1>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md">
                {openAiAnswer}
              </div>
              </>
            )}
            <div className="flex gap-4 flex-col">
              <h1 className="text-xl font-bold">Period-wise usage</h1>
            <PredictionTable predictions={predictions} />
            </div>
          </div>
        ) : (
          <div className="grow flex justify-center items-center">
            Please enter site details to see predictions.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
