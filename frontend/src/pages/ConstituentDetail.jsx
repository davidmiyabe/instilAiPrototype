import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { constituentsAPI, contributionsAPI, interactionsAPI } from '../services/api'

export default function ConstituentDetail() {
  const { id } = useParams()
  const [constituent, setConstituent] = useState(null)
  const [summary, setSummary] = useState(null)
  const [contributions, setContributions] = useState([])
  const [interactions, setInteractions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      constituentsAPI.get(id),
      constituentsAPI.getSummary(id),
      contributionsAPI.list({ constituent_id: id }),
      interactionsAPI.list({ constituent_id: id, limit: 10 }),
    ])
      .then(([constRes, summaryRes, contribRes, intRes]) => {
        setConstituent(constRes.data)
        setSummary(summaryRes.data)
        setContributions(contribRes.data)
        setInteractions(intRes.data)
      })
      .catch((error) => console.error('Error loading constituent:', error))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading">Loading constituent...</div>
  if (!constituent) return <div className="error">Constituent not found</div>

  return (
    <div className="constituent-detail">
      <div className="page-header">
        <div>
          <Link to="/constituents" className="back-link">
            ← Back to Constituents
          </Link>
          <h1>
            {constituent.first_name} {constituent.last_name}
          </h1>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h2>Contact Information</h2>
          <div className="info-row">
            <span className="label">Email:</span>
            <span>{constituent.email}</span>
          </div>
          <div className="info-row">
            <span className="label">Phone:</span>
            <span>{constituent.phone}</span>
          </div>
          <div className="info-row">
            <span className="label">Address:</span>
            <span>
              {constituent.address}
              <br />
              {constituent.city}, {constituent.state} {constituent.zip_code}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Type:</span>
            <span className={`badge badge-${constituent.constituent_type}`}>
              {constituent.constituent_type}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Status:</span>
            <span className={`status-${constituent.status}`}>
              {constituent.status}
            </span>
          </div>
        </div>

        <div className="detail-card">
          <h2>Giving Summary</h2>
          <div className="info-row">
            <span className="label">Total Contributions:</span>
            <span className="highlight">
              ${Number(summary?.total_contributions || 0).toLocaleString()}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Number of Gifts:</span>
            <span>{summary?.contribution_count || 0}</span>
          </div>
          <div className="info-row">
            <span className="label">Average Gift:</span>
            <span>
              ${Number(summary?.average_contribution || 0).toLocaleString()}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Last Gift Date:</span>
            <span>
              {summary?.last_contribution_date
                ? new Date(summary.last_contribution_date).toLocaleDateString()
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {constituent.notes && (
        <div className="detail-card">
          <h2>Notes</h2>
          <p>{constituent.notes}</p>
        </div>
      )}

      <div className="detail-card">
        <h2>Recent Contributions</h2>
        {contributions.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Type</th>
                <th>Campaign</th>
              </tr>
            </thead>
            <tbody>
              {contributions.map((contribution) => (
                <tr key={contribution.contribution_id}>
                  <td>
                    {new Date(contribution.contribution_date).toLocaleDateString()}
                  </td>
                  <td className="highlight">
                    ${Number(contribution.amount).toLocaleString()}
                  </td>
                  <td>{contribution.contribution_type}</td>
                  <td>{contribution.campaign || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="no-data">No contributions recorded</p>
        )}
      </div>

      <div className="detail-card">
        <h2>Recent Interactions</h2>
        {interactions.length > 0 ? (
          <div className="activity-list">
            {interactions.map((interaction) => (
              <div key={interaction.interaction_id} className="activity-item">
                <div className="activity-title">{interaction.subject}</div>
                <div className="activity-meta">
                  {interaction.interaction_type} •{' '}
                  {new Date(interaction.interaction_date).toLocaleDateString()}
                </div>
                {interaction.notes && (
                  <div className="activity-notes">{interaction.notes}</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">No interactions recorded</p>
        )}
      </div>
    </div>
  )
}
