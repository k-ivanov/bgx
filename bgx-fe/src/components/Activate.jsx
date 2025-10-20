import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { activateAccount } from '../api/api'
import './Activate.css'

function Activate() {
  const navigate = useNavigate()
  const location = useLocation()
  const [activationCode, setActivationCode] = useState(location.state?.activationCode || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [userData, setUserData] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await activateAccount(activationCode)
      setSuccess(true)
      setUserData(response.user)
      
      // Store tokens
      if (response.access) {
        localStorage.setItem('access_token', response.access)
        localStorage.setItem('refresh_token', response.refresh)
      }
      
      // Redirect after 3 seconds
      setTimeout(() => {
        navigate('/')
      }, 3000)
    } catch (err) {
      console.error('Activation error:', err)
      if (err.response?.data?.activation_code) {
        setError(err.response.data.activation_code[0])
      } else if (err.response?.data?.message) {
        setError(err.response.data.message)
      } else {
        setError('Activation failed. Please check your code and try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (success && userData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Account Activated!
          </h2>
          <p className="text-gray-600 mb-6">
            Welcome, <strong>{userData.first_name} {userData.last_name}</strong>!
          </p>
          <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6 text-left">
            <p className="text-sm text-green-800">
              ✨ Your account has been successfully activated. You are now logged in!
            </p>
          </div>
          <p className="text-gray-500 text-sm">
            Redirecting to home page...
          </p>
          <div className="mt-6">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition shadow-sm"
            >
              Go to Home Now →
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🔑</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Activate Your Account
          </h1>
          <p className="text-gray-600">
            Enter the activation code you received during registration
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Activation Code
            </label>
            <input
              type="text"
              value={activationCode}
              onChange={(e) => setActivationCode(e.target.value)}
              placeholder="Enter your activation code"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent font-mono text-lg"
            />
            <p className="text-gray-500 text-xs mt-2">
              This is the code you received after registration
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !activationCode}
            className="w-full py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Activating...' : 'Activate Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm mb-2">
            Don't have an activation code?
          </p>
          <button
            onClick={() => navigate('/register')}
            className="text-primary font-semibold hover:underline text-sm"
          >
            Register for a new account
          </button>
          <br />
          <button
            onClick={() => navigate('/')}
            className="mt-4 text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  )
}

export default Activate

