import { useEffect, useState } from "react";
import "./App.css";
import { postGrammar } from "./api";
import Mermaid from "mermaid";

function App() {
  const [grammar, setGrammar] = useState("");
  const [mermaidChart, setMermaidChart] = useState<string>("");

  useEffect(() => {
    Mermaid.initialize({
      startOnLoad: true,
      securityLevel: "loose",
      theme: "forest",
      logLevel: 5,
    });
  }, []);

  useEffect(() => {
    if (mermaidChart) {
      const elements = document.querySelectorAll<HTMLElement>(".mermaid");
      Mermaid.init(undefined, elements);
    }
    console.log("Contenido Mermaid:", mermaidChart);
  }, [mermaidChart]);

  const onConvertDFA = async () => {
    try {
      const response = await postGrammar(grammar, "/convert-dfa");
      let mermaidOutput = response.data.formatted;
      setMermaidChart(mermaidOutput);
    } catch (e) {
      alert("Something went wrong: " + e);
    }
  };

  const onConvertPDA = async () => {
    try {
      const response = await postGrammar(grammar, "/convert");
      let mermaidOutput = response.data.formatted;
      setMermaidChart(mermaidOutput);
    } catch (e) {
      alert("Something went wrong: " + e);
    }
  };

  const onConvertItemsA = async () => {
    try {
      const response = await postGrammar(grammar, "/items");
      let mermaidOutput = response.data.formatted;
      mermaidOutput = mermaidOutput.replaceAll(';', '\n    ');
      console.log(mermaidOutput.replaceAll(';', '\n    '))
      setMermaidChart(mermaidOutput);
    } catch (e) {
      alert("Something went wrong: " + e);
    }
  };

  return (
    <>
      <h1>Convert CFG to Valid Items Automaton</h1>
      <div className="flex">
        <div>
          <textarea
            rows={10}
            cols={50}
            placeholder="Escribe aquí la gramática..."
            onChange={(e) => setGrammar(e.target.value)}
          ></textarea>
          <br />
          {/*sirven solo con tokens de 1 caracter*/}
	   {/* <button onClick={onConvertPDA}>Convert to PDA</button>*/}
	   {/* <button onClick={onConvertDFA}>Convert to DFA</button>*/}
          <button onClick={onConvertItemsA}>Convert to Items Automaton</button>
        </div>
        <div
          key={mermaidChart}
          className="mermaid h-100 w-100"
          dangerouslySetInnerHTML={{ __html: mermaidChart }}
        ></div>
      </div>
    </>
  );
}

export default App;
