import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register } from '../api/api'
import './Register.css'

function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [activationCode, setActivationCode] = useState(null)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Basic validation
    if (formData.password !== formData.password2) {
      setError({ password: ["Passwords don't match"] })
      setLoading(false)
      return
    }

    if (formData.password.length < 8) {
      setError({ password: ["Password must be at least 8 characters"] })
      setLoading(false)
      return
    }

    try {
      const response = await register(formData)
      setSuccess(true)
      setActivationCode(response.activation_code)
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

  if (success && activationCode) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Registration Successful!
            </h2>
            <p className="text-gray-600">
              Your account has been created. Please save your activation code.
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <p className="text-blue-900 text-sm mb-2 font-semibold">Your Activation Code:</p>
            <div className="bg-white border border-blue-200 rounded p-3 flex items-center justify-between">
              <code className="text-lg font-mono text-gray-900 break-all">
                {activationCode}
              </code>
              <button
                onClick={copyActivationCode}
                className="ml-2 px-3 py-1 bg-primary text-white rounded hover:bg-primary-dark transition text-sm flex-shrink-0"
              >
                📋 Copy
              </button>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>Important:</strong> Save this code securely. You'll need it to activate your account.
            </p>
          </div>

          <button
            onClick={() => navigate('/activate', { state: { activationCode } })}
            className="w-full py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition shadow-sm"
          >
            Continue to Activation →
          </button>

          <button
            onClick={() => navigate('/')}
            className="w-full mt-3 py-3 text-gray-600 hover:text-gray-900 transition"
          >
            Skip for Now
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
          <p className="text-gray-600">Join the BGX Racing Platform</p>
        </div>

        {error?.general && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <p className="text-sm text-red-800">{error.general[0]}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
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
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
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
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
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
              Must be at least 8 characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              required
              minLength="8"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary-dark transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-primary font-semibold hover:underline"
            >
              Sign In
            </button>
          </p>
          <button
            onClick={() => navigate('/')}
            className="mt-2 text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  )
}

export default Register

