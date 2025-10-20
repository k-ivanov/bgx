import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { matchRider, claimAccount, register } from '../api/api'
import './Register.css'

function Register({ embedded = false, onSuccess = null }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  
  // Multi-step form state
  const [step, setStep] = useState(0) // 0: Choose, 1: Match/Register, 2: Select, 3: Claim, 4: Success
  const [registrationType, setRegistrationType] = useState(null) // 'new' or 'claim'
  
  // Step 1 (Match): Match data
  const [matchData, setMatchData] = useState({
    first_name: '',
    last_name: '',
    license_number: '',
    date_of_birth: '',
  })
  
  // Step 2: Matched riders
  const [matchedRiders, setMatchedRiders] = useState([])
  const [selectedRider, setSelectedRider] = useState(null)
  
  // Step 3: Claim data
  const [claimData, setClaimData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  })
  
  // Normal registration data
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  })
  
  // Step 4: Success data
  const [activationCode, setActivationCode] = useState(null)
  const [claimedUser, setClaimedUser] = useState(null)
  
  // UI state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [matchMessage, setMatchMessage] = useState(null)

  // Step 1: Handle match form
  const handleMatchChange = (e) => {
    setMatchData({
      ...matchData,
      [e.target.name]: e.target.value
    })
  }

  const handleMatchSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setMatchMessage(null)

    try {
      const response = await matchRider(matchData)
      setMatchedRiders(response.matches || [])
      setMatchMessage(response.message)
      
      if (response.matches && response.matches.length > 0) {
        setStep(2)
      } else {
        setError({ general: [response.message || 'No matching riders found'] })
      }
    } catch (err) {
      console.error('Match error:', err)
      if (err.response?.data) {
        setError(err.response.data)
      } else {
        setError({ general: ['Failed to search for riders. Please try again.'] })
      }
    } finally {
      setLoading(false)
    }
  }

  // Step 2: Select rider
  const handleSelectRider = (rider) => {
    setSelectedRider(rider)
    setStep(3)
  }

  // Step 3: Handle claim form
  const handleClaimChange = (e) => {
    setClaimData({
      ...claimData,
      [e.target.name]: e.target.value
    })
  }

  const handleClaimSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Basic validation
    if (claimData.password !== claimData.password2) {
      setError({ password: ["Passwords don't match"] })
      setLoading(false)
      return
    }

    if (claimData.password.length < 8) {
      setError({ password: ["Password must be at least 8 characters"] })
      setLoading(false)
      return
    }

    try {
      const response = await claimAccount({
        rider_id: selectedRider.id,
        username: claimData.username,
        email: claimData.email,
        password: claimData.password,
        password2: claimData.password2,
      })
      
      setActivationCode(response.activation_code)
      setClaimedUser(response.user)
      setStep(4)
    } catch (err) {
      console.error('Claim error:', err)
      if (err.response?.data) {
        setError(err.response.data)
      } else {
        setError({ general: ['Failed to claim account. Please try again.'] })
      }
    } finally {
      setLoading(false)
    }
  }

  // Normal registration handler
  const handleRegisterChange = (e) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value
    })
  }

  const handleRegisterSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Basic validation
    if (registerData.password !== registerData.password2) {
      setError({ password: ["Passwords don't match"] })
      setLoading(false)
      return
    }

    if (registerData.password.length < 8) {
      setError({ password: ["Password must be at least 8 characters"] })
      setLoading(false)
      return
    }

    try {
      const response = await register(registerData)
      setActivationCode(response.activation_code)
      setStep(4)
    } catch (err) {
      console.error('Registration error:', err)
      if (err.response?.data) {
        setError(err.response.data)
      } else {
        setError({ general: ['Registration failed. Please try again.'] })
      }
    } finally {
      setLoading(false)
    }
  }

  const copyActivationCode = () => {
    navigator.clipboard.writeText(activationCode)
    alert('Activation code copied to clipboard!')
  }

  // Step 4: Success screen
  if (step === 4 && activationCode) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="bg-white rounded-2xl shadow-large p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {t('auth.register.success.title')}
            </h2>
            <p className="text-gray-600">
              {t('auth.register.success.message')}
            </p>
          </div>

          <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 mb-6">
            <p className="text-primary-900 text-sm mb-2 font-semibold">
              {t('auth.register.success.codeLabel')}
            </p>
            <div className="bg-white border border-primary-200 rounded p-3 flex items-center justify-between">
              <code className="text-lg font-mono text-gray-900 break-all">
                {activationCode}
              </code>
              <button
                onClick={copyActivationCode}
                className="ml-2 px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark transition text-sm flex-shrink-0"
              >
                📋 {t('auth.register.success.copy')}
              </button>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>{t('auth.register.success.warning', 'Important:')}</strong>
            </p>
          </div>

          <button
            onClick={() => {
              if (embedded && onSuccess) {
                onSuccess(activationCode)
              } else {
                navigate('/activate', { state: { activationCode } })
              }
            }}
            className="w-full py-3 bg-gradient-to-r from-primary to-primary-400 text-white rounded-lg font-semibold hover:shadow-lg transition shadow-[0_4px_15px_-3px_rgba(37,99,235,0.3)]"
          >
            {t('auth.register.success.continue')}
          </button>

          {!embedded && (
            <button
              onClick={() => navigate('/')}
              className="w-full mt-3 py-3 text-gray-600 hover:text-gray-900 transition"
            >
              {t('auth.register.backToHome')}
            </button>
          )}
        </div>
      </div>
    )
  }

  // Step 3: Claim account form
  if (step === 3 && selectedRider) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="bg-white rounded-2xl shadow-large p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.register.claim.title')}</h1>
            <p className="text-gray-600">{t('auth.register.claim.subtitle')}</p>
          </div>

          {/* Selected rider info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-900 font-semibold mb-1">{t('auth.register.claim.claimingFor')}</p>
            <p className="text-lg font-bold text-blue-900">
              {selectedRider.first_name} {selectedRider.last_name}
            </p>
            {selectedRider.license_number && (
              <p className="text-sm text-blue-700">{t('auth.register.select.license')}: {selectedRider.license_number}</p>
            )}
            {selectedRider.club && (
              <p className="text-sm text-blue-700">{t('auth.register.select.club')}: {selectedRider.club}</p>
            )}
          </div>

          {error?.general && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <p className="text-sm text-red-800">{error.general[0]}</p>
            </div>
          )}

          <form onSubmit={handleClaimSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.claim.usernameLabel')}
              </label>
              <input
                type="text"
                name="username"
                value={claimData.username}
                onChange={handleClaimChange}
                required
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.username ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.username && (
                <p className="text-red-500 text-sm mt-1">{error.username[0]}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.claim.emailLabel')}
              </label>
              <input
                type="email"
                name="email"
                value={claimData.email}
                onChange={handleClaimChange}
                required
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.email && (
                <p className="text-red-500 text-sm mt-1">{error.email[0]}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.claim.passwordLabel')}
              </label>
              <input
                type="password"
                name="password"
                value={claimData.password}
                onChange={handleClaimChange}
                required
                minLength="8"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.password ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.password && (
                <p className="text-red-500 text-sm mt-1">{error.password[0]}</p>
              )}
              <p className="text-gray-500 text-xs mt-1">
                {t('auth.register.claim.passwordHint')}
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.claim.confirmPasswordLabel')}
              </label>
              <input
                type="password"
                name="password2"
                value={claimData.password2}
                onChange={handleClaimChange}
                required
                minLength="8"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
              >
                ← {t('auth.register.claim.backButton')}
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 bg-gradient-to-r from-primary to-primary-400 text-white rounded-lg font-semibold hover:shadow-lg transition shadow-[0_4px_15px_-3px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? t('auth.register.claim.claiming') : t('auth.register.claim.claimButton')}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← {t('auth.register.claim.cancelButton')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Step 2: Select matched rider
  if (step === 2 && matchedRiders.length > 0) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="bg-white rounded-2xl shadow-large p-8 max-w-2xl w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.register.select.title')}</h1>
            <p className="text-gray-600">{t('auth.register.select.subtitle', { count: matchedRiders.length })}</p>
          </div>

          <div className="space-y-3 mb-6">
            {matchedRiders.map((rider) => (
              <button
                key={rider.id}
                onClick={() => handleSelectRider(rider)}
                className="w-full text-left p-5 border-2 border-gray-200 rounded-lg hover:border-primary hover:bg-primary-50 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary">
                      {rider.first_name} {rider.last_name}
                    </h3>
                    <div className="mt-1 space-y-1">
                      {rider.license_number && (
                        <p className="text-sm text-gray-600">
                          🏍️ {t('auth.register.select.license')}: <span className="font-semibold">{rider.license_number}</span>
                        </p>
                      )}
                      {rider.club && (
                        <p className="text-sm text-gray-600">
                          🏁 {t('auth.register.select.club')}: <span className="font-semibold">{rider.club}</span>
                        </p>
                      )}
                      {rider.is_licensed && (
                        <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
                          ✓ {t('auth.register.select.licensed')}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-primary text-2xl group-hover:scale-110 transition-transform">
                    →
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              ← {t('auth.register.select.searchAgain')}
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 py-3 text-gray-600 hover:text-gray-900 transition"
            >
              {t('auth.register.select.cancel')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Step 0: Choose registration type
  if (step === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="bg-white rounded-2xl shadow-large p-8 max-w-2xl w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.register.choose.title')}</h1>
            <p className="text-gray-600">{t('auth.register.choose.subtitle')}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Claim existing profile */}
            <button
              onClick={() => {
                setRegistrationType('claim')
                setStep(1)
              }}
              className="p-8 border-2 border-gray-200 rounded-xl hover:border-primary hover:bg-primary-50 transition-all group text-left"
            >
              <div className="text-5xl mb-4">🏍️</div>
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary mb-2">
                {t('auth.register.choose.claimTitle')}
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                {t('auth.register.choose.claimDescription')}
              </p>
              <div className="flex items-center text-primary font-semibold text-sm">
                {t('auth.register.choose.claimButton')} →
              </div>
            </button>

            {/* New registration */}
            <button
              onClick={() => {
                setRegistrationType('new')
                setStep(1)
              }}
              className="p-8 border-2 border-gray-200 rounded-xl hover:border-primary hover:bg-primary-50 transition-all group text-left"
            >
              <div className="text-5xl mb-4">✨</div>
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary mb-2">
                {t('auth.register.choose.newTitle')}
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                {t('auth.register.choose.newDescription')}
              </p>
              <div className="flex items-center text-primary font-semibold text-sm">
                {t('auth.register.choose.newButton')} →
              </div>
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← {t('common.back')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Step 1: Normal registration form
  if (step === 1 && registrationType === 'new') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="bg-white rounded-2xl shadow-large p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.register.title')}</h1>
            <p className="text-gray-600">{t('auth.register.subtitle')}</p>
          </div>

          {error?.general && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <p className="text-sm text-red-800">{error.general[0]}</p>
            </div>
          )}

          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {t('auth.register.firstName')}
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={registerData.first_name}
                  onChange={handleRegisterChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {t('auth.register.lastName')}
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={registerData.last_name}
                  onChange={handleRegisterChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.username')}
              </label>
              <input
                type="text"
                name="username"
                value={registerData.username}
                onChange={handleRegisterChange}
                required
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.username ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.username && (
                <p className="text-red-500 text-sm mt-1">{error.username[0]}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.email')}
              </label>
              <input
                type="email"
                name="email"
                value={registerData.email}
                onChange={handleRegisterChange}
                required
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.email && (
                <p className="text-red-500 text-sm mt-1">{error.email[0]}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.password')}
              </label>
              <input
                type="password"
                name="password"
                value={registerData.password}
                onChange={handleRegisterChange}
                required
                minLength="8"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent ${
                  error?.password ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {error?.password && (
                <p className="text-red-500 text-sm mt-1">{error.password[0]}</p>
              )}
              <p className="text-gray-500 text-xs mt-1">
                {t('auth.register.passwordRequirement')}
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('auth.register.confirmPassword')}
              </label>
              <input
                type="password"
                name="password2"
                value={registerData.password2}
                onChange={handleRegisterChange}
                required
                minLength="8"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setStep(0)
                  setRegistrationType(null)
                }}
                className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
              >
                ← {t('common.back')}
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 bg-gradient-to-r from-primary to-primary-400 text-white rounded-lg font-semibold hover:shadow-lg transition shadow-[0_4px_15px_-3px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? t('auth.register.submitting') : t('auth.register.submit')}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← {t('auth.register.backToHome')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Step 1: Match rider form
  if (step === 1 && registrationType === 'claim') {
    return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="bg-white rounded-2xl shadow-large p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('auth.register.match.title')}</h1>
          <p className="text-gray-600">{t('auth.register.match.subtitle')}</p>
        </div>

        {error?.general && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <p className="text-sm text-red-800">{error.general[0]}</p>
            <p className="text-xs text-red-700 mt-1">
              {t('auth.register.match.contactAdmin')}
            </p>
          </div>
        )}

        <form onSubmit={handleMatchSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('auth.register.match.firstNameLabel')} *
            </label>
            <input
              type="text"
              name="first_name"
              value={matchData.first_name}
              onChange={handleMatchChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('auth.register.match.lastNameLabel')} *
            </label>
            <input
              type="text"
              name="last_name"
              value={matchData.last_name}
              onChange={handleMatchChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('auth.register.match.licenseLabel')}
            </label>
            <input
              type="text"
              name="license_number"
              value={matchData.license_number}
              onChange={handleMatchChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder={t('auth.register.match.licensePlaceholder')}
            />
            <p className="text-gray-500 text-xs mt-1">
              {t('auth.register.match.licenseHint')}
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('auth.register.match.dobLabel')}
            </label>
            <input
              type="date"
              name="date_of_birth"
              value={matchData.date_of_birth}
              onChange={handleMatchChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => {
                setStep(0)
                setRegistrationType(null)
              }}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
            >
              ← {t('common.back')}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 bg-gradient-to-r from-primary to-primary-400 text-white rounded-lg font-semibold hover:shadow-lg transition shadow-[0_4px_15px_-3px_rgba(37,99,235,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? t('auth.register.match.searching') : t('auth.register.match.searchButton')}
            </button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            ← {t('auth.register.match.backToHome')}
          </button>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            💡 {t('auth.register.match.helpText')}
          </p>
        </div>
      </div>
    </div>
    )
  }

  // Default: Should not reach here
  return null
}

export default Register
