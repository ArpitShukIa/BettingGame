import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './components/App';
import reportWebVitals from './reportWebVitals';

import {DAppProvider, Rinkeby} from "@usedapp/core";
import {getDefaultProvider} from "ethers";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <DAppProvider config={{
            readOnlyChainId: Rinkeby.chainId,
            readOnlyUrls: {
                [Rinkeby.chainId]: getDefaultProvider('rinkeby'),
            }
        }}>
            <App/>
        </DAppProvider>
    </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
