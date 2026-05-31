import { useState } from 'react'
import { ScenarioPanel } from './components/ScenarioPanel/ScenarioPanel'
import { DEFAULT_PANEL_STATE } from './types/pricing'
import type { AppMode } from './types/pricing'
import styles from './App.module.css'

export default function App() {
  const [mode, setMode] = useState<AppMode>('single')

  const toggleMode = () => {
    setMode(prev => (prev === 'single' ? 'comparison' : 'single'))
  }

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1 className={styles.title}>Home Loan Pricing</h1>
        <button
          type="button"
          className={styles.modeToggle}
          onClick={toggleMode}
          aria-pressed={mode === 'comparison'}
        >
          {mode === 'single' ? 'Compare Two Scenarios' : 'Single Scenario'}
        </button>
      </header>

      <main className={mode === 'comparison' ? styles.comparisonLayout : styles.singleLayout}>
        <section aria-label="Scenario A">
          <ScenarioPanel
            state={DEFAULT_PANEL_STATE('a')}
            onResult={() => {}}
            onError={() => {}}
            onLoading={() => {}}
          />
        </section>

        {mode === 'comparison' && (
          <section aria-label="Scenario B">
            <ScenarioPanel
              state={DEFAULT_PANEL_STATE('b')}
              onResult={() => {}}
              onError={() => {}}
              onLoading={() => {}}
            />
          </section>
        )}
      </main>
    </div>
  )
}
