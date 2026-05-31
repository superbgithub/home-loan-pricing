import { useForm } from 'react-hook-form'
import type { ScenarioFormValues, ProductType } from '../../types/pricing'
import { ArmFields } from './ArmFields'
import styles from './ScenarioForm.module.css'

interface ScenarioFormProps {
  defaultValues: ScenarioFormValues
  onSubmit: (values: ScenarioFormValues) => void
  disabled?: boolean
}

export function ScenarioForm({ defaultValues, onSubmit, disabled }: ScenarioFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors },
  } = useForm<ScenarioFormValues>({ defaultValues })

  const productType = watch('productType')

  const handleProductToggle = (type: ProductType) => {
    setValue('productType', type)
    setValue('annualRate', '')
    setValue('initialRate', '')
  }

  const isArm = productType === 'arm'

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form} noValidate>
      <div className={styles.toggle} role="group" aria-label="Product type">
        <button
          type="button"
          className={!isArm ? styles.activeToggle : styles.inactiveToggle}
          onClick={() => handleProductToggle('fixed')}
          aria-pressed={!isArm}
        >
          Fixed Rate
        </button>
        <button
          type="button"
          className={isArm ? styles.activeToggle : styles.inactiveToggle}
          onClick={() => handleProductToggle('arm')}
          aria-pressed={isArm}
        >
          Adjustable Rate (ARM)
        </button>
      </div>

      <div className={styles.field}>
        <label htmlFor="homePrice">Home Price</label>
        <input
          id="homePrice"
          type="number"
          step="0.01"
          min={0}
          aria-label="Home Price"
          {...register('homePrice', {
            required: 'Home Price is required',
            min: { value: 0.01, message: 'Home Price must be greater than 0' },
          })}
        />
        {errors.homePrice && <span className={styles.error}>{errors.homePrice.message}</span>}
      </div>

      <div className={styles.field}>
        <label htmlFor="downPayment">Down Payment</label>
        <input
          id="downPayment"
          type="text"
          aria-label="Down Payment"
          placeholder="e.g. 80000 or 20%"
          {...register('downPayment', { required: 'Down Payment is required' })}
        />
        {errors.downPayment && <span className={styles.error}>{errors.downPayment.message}</span>}
      </div>

      <div className={styles.field}>
        <label htmlFor="termYears">Loan Term</label>
        <select id="termYears" aria-label="Loan Term" {...register('termYears', { required: true })}>
          <option value="10">10 years</option>
          <option value="15">15 years</option>
          <option value="20">20 years</option>
          <option value="30">30 years</option>
        </select>
      </div>

      {!isArm && (
        <div className={styles.field}>
          <label htmlFor="annualRate">Annual Rate (%)</label>
          <input
            id="annualRate"
            type="number"
            step="0.001"
            aria-label="Annual Rate"
            {...register('annualRate', {
              required: 'Annual Rate is required',
              min: { value: 0, message: 'Rate must be between 0 and 30' },
              max: { value: 30, message: 'Rate must be between 0 and 30' },
            })}
          />
          {errors.annualRate && <span className={styles.error}>{errors.annualRate.message}</span>}
        </div>
      )}

      {isArm && (
        <div className={styles.field}>
          <label htmlFor="initialRate">Initial Rate (%)</label>
          <input
            id="initialRate"
            type="number"
            step="0.001"
            aria-label="Initial Rate"
            {...register('initialRate', {
              required: 'Initial Rate is required',
              min: { value: 0, message: 'Rate must be between 0 and 30' },
              max: { value: 30, message: 'Rate must be between 0 and 30' },
            })}
          />
          {errors.initialRate && <span className={styles.error}>{errors.initialRate.message}</span>}
        </div>
      )}

      {isArm && <ArmFields control={control} errors={errors} />}

      <button type="submit" className={styles.submit} disabled={disabled}>
        Get Quote
      </button>
    </form>
  )
}
