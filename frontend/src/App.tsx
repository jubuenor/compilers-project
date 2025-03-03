import { useEffect, useState } from "react";
import "./App.css";
import { postGrammar } from "./api";
import Mermaid from "mermaid";

//interface Response {
//    raw: string;
//    formatted: string;
//}

function App() {
    const [grammar, setGrammar] = useState("");
    const [mermaidChart, setMermaidChart] = useState<string>("graph LR; Q1-->|a, S; SX| Q1; Q1-->|b, S; SY, λ| Q1; Q1-->|b, X; λ| Q1; Q1-->|a, Y; λ| Q1; Q0-->|λ, ε; Sε| Q1; Q1-->|λ, ε; ε| Q2;");

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
            Mermaid.contentLoaded();
        }
        console.log(mermaidChart);
    }, [mermaidChart]);

    const onSubmit = async () => {
        try {
            console.log(grammar);
            const response = await postGrammar(grammar);
            setMermaidChart("graph LR;\n" + response.data.formatted.replace("\n",""));
        } catch (e) {
            alert("Something went wrong" + e);
        }
    };

    return (
        <>
            <h1>Convert CFG to PDA</h1>
            <div className="flex">
                <div>
                    <textarea
                        rows={10}
                        cols={50}
                        onChange={(
                            e: React.ChangeEvent<HTMLTextAreaElement>,
                        ) => setGrammar(e.target.value)}
                    >
                    </textarea>
                    <br />
                    <button onClick={() => onSubmit()}>
                        Convert
                    </button>
                </div>
                <div
                    className="mermaid h-100 w-100"
                    dangerouslySetInnerHTML={{
                        __html: mermaidChart ? mermaidChart : "",
                    }}
                >
                </div>
            </div>
        </>
    );
}

export default App;
