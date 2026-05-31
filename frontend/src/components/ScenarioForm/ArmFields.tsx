import type { Control, FieldErrors } from 'react-hook-form'
import { Controller } from 'react-hook-form'
import type { ScenarioFormValues } from '../../types/pricing'
import styles from './ScenarioForm.module.css'

interface ArmFieldsProps {
  control: Control<ScenarioFormValues>
  errors: FieldErrors<ScenarioFormValues>
}

export function ArmFields({ control, errors }: ArmFieldsProps) {
  return (
    <fieldset className={styles.fieldset}>
      <legend>ARM Parameters</legend>

      <Controller
        name="armParams.fixedPeriodYears"
        control={control}
        rules={{ required: 'Fixed period is required', min: { value: 1, message: 'Min 1 year' } }}
        render={({ field }) => (
          <div className={styles.field}>
            <label htmlFor="fixedPeriodYears">Fixed Period (years)</label>
            <input id="fixedPeriodYears" type="number" min={1} {...field} />
            {errors.armParams?.fixedPeriodYears && (
              <span className={styles.error}>{errors.armParams.fixedPeriodYears.message}</span>
            )}
          </div>
        )}
      />

      <Controller
        name="armParams.adjustmentPeriodYears"
        control={control}
        rules={{ required: 'Adjustment interval is required', min: { value: 1, message: 'Min 1 year' } }}
        render={({ field }) => (
          <div className={styles.field}>
            <label htmlFor="adjustmentPeriodYears">Adjustment Interval (years)</label>
            <input id="adjustmentPeriodYears" type="number" min={1} {...field} />
            {errors.armParams?.adjustmentPeriodYears && (
              <span className={styles.error}>{errors.armParams.adjustmentPeriodYears.message}</span>
            )}
          </div>
        )}
      />

      <Controller
        name="armParams.initialCap"
        control={control}
        rules={{ required: 'Initial cap is required', min: { value: 0, message: 'Min 0' } }}
        render={({ field }) => (
          <div className={styles.field}>
            <label htmlFor="initialCap">Initial Cap (%)</label>
            <input id="initialCap" type="number" step="0.01" min={0} {...field} />
            {errors.armParams?.initialCap && (
              <span className={styles.error}>{errors.armParams.initialCap.message}</span>
            )}
          </div>
        )}
      />

      <Controller
        name="armParams.periodicCap"
        control={control}
        rules={{
          required: 'Periodic cap is required',
          min: { value: 0.01, message: 'Must be > 0' },
          validate: (v, formValues) =>
            parseFloat(v) <= parseFloat(formValues.armParams.lifetimeCap || '999') ||
            'Periodic cap must be ≤ lifetime cap',
        }}
        render={({ field }) => (
          <div className={styles.field}>
            <label htmlFor="periodicCap">Periodic Cap (%)</label>
            <input id="periodicCap" type="number" step="0.01" min={0} {...field} />
            {errors.armParams?.periodicCap && (
              <span className={styles.error}>{errors.armParams.periodicCap.message}</span>
            )}
          </div>
        )}
      />

      <Controller
        name="armParams.lifetimeCap"
        control={control}
        rules={{ required: 'Lifetime cap is required', min: { value: 0.01, message: 'Must be > 0' } }}
        render={({ field }) => (
          <div className={styles.field}>
            <label htmlFor="lifetimeCap">Lifetime Cap (%)</label>
            <input id="lifetimeCap" type="number" step="0.01" min={0} {...field} />
            {errors.armParams?.lifetimeCap && (
              <span className={styles.error}>{errors.armParams.lifetimeCap.message}</span>
            )}
          </div>
        )}
      />
    </fieldset>
  )
}
