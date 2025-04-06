import { PVForecastForm } from "./components/PVForecastForm";
import { Separator } from "./components/ui/separator";
import { useState } from "react";
import { PredictionTable } from "./components/PredictionTable";
import { PredictionChart } from "./components/PredicitionChart";

function App() {
  const [predictions, setPredictions] = useState(null);
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
          <div className="grow flex flex-col justify-between w-2/5 p-20">
            <PredictionChart predictions={predictions} />
            <PredictionTable predictions={predictions} />
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
