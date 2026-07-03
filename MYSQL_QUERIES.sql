-- MySQL Query Reference for Loan Approval System
-- Database: loan_approval
-- Tables: applications, decisions

-- ============================================
-- CONNECTING TO THE DATABASE
-- ============================================
-- mysql -h localhost -u root -pTek@12345 loan_approval


-- ============================================
-- 1. VIEW ALL APPLICATIONS
-- ============================================
SELECT
    applicant_id,
    applicant_name,
    status,
    risk_score,
    income,
    credit_score,
    loan_amount,
    created_at
FROM applications
ORDER BY created_at DESC;


-- ============================================
-- 2. VIEW ALL DECISIONS
-- ============================================
SELECT
    applicant_id,
    application_status,
    risk_score,
    confidence_level,
    processing_duration_seconds,
    created_at
FROM decisions
ORDER BY created_at DESC;


-- ============================================
-- 3. SEARCH SPECIFIC APPLICANT
-- ============================================
SELECT * FROM applications
WHERE applicant_id = 'APP001';

SELECT * FROM decisions
WHERE applicant_id = 'APP001';


-- ============================================
-- 4. JOIN APPLICATIONS WITH DECISIONS
-- ============================================
SELECT
    a.applicant_id,
    a.applicant_name,
    a.status as app_status,
    a.risk_score as app_risk_score,
    d.application_status,
    d.confidence_level,
    d.risk_score as decision_risk_score,
    a.created_at
FROM applications a
LEFT JOIN decisions d ON a.applicant_id = d.applicant_id
ORDER BY a.created_at DESC;


-- ============================================
-- 5. STATISTICS BY APPLICATION STATUS
-- ============================================
SELECT
    COUNT(*) as total_applications,
    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN status = 'MANUAL_REVIEW' THEN 1 ELSE 0 END) as manual_review,
    SUM(CASE WHEN status = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed
FROM applications;


-- ============================================
-- 6. HIGH-RISK APPLICATIONS (risk_score > 60)
-- ============================================
SELECT
    applicant_id,
    applicant_name,
    risk_score,
    income,
    credit_score,
    loan_amount,
    status,
    created_at
FROM applications
WHERE risk_score > 60
ORDER BY risk_score DESC;


-- ============================================
-- 7. LOW-CONFIDENCE DECISIONS (< 70%)
-- ============================================
SELECT
    applicant_id,
    confidence_level,
    risk_score,
    application_status,
    processing_duration_seconds
FROM decisions
WHERE confidence_level < 70
ORDER BY confidence_level ASC;


-- ============================================
-- 8. APPLICATIONS WITHIN DATE RANGE
-- ============================================
SELECT
    applicant_id,
    applicant_name,
    status,
    created_at
FROM applications
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY created_at DESC;


-- ============================================
-- 9. APPROVED APPLICATIONS SUMMARY
-- ============================================
SELECT
    a.applicant_id,
    a.applicant_name,
    a.income,
    a.credit_score,
    d.confidence_level,
    d.risk_score,
    a.created_at
FROM applications a
JOIN decisions d ON a.applicant_id = d.applicant_id
WHERE a.status = 'APPROVED'
ORDER BY d.confidence_level DESC;


-- ============================================
-- 10. REJECTED APPLICATIONS WITH REASONS
-- ============================================
SELECT
    a.applicant_id,
    a.applicant_name,
    a.status,
    a.error,
    d.application_status,
    d.final_explanation,
    a.created_at
FROM applications a
LEFT JOIN decisions d ON a.applicant_id = d.applicant_id
WHERE a.status = 'REJECTED'
ORDER BY a.created_at DESC;


-- ============================================
-- 11. AVERAGE METRICS BY EMPLOYMENT TYPE
-- ============================================
SELECT
    employment_type,
    COUNT(*) as count,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    ROUND(AVG(credit_score), 2) as avg_credit_score,
    ROUND(AVG(income), 2) as avg_income,
    ROUND(AVG(loan_amount), 2) as avg_loan_amount
FROM applications
GROUP BY employment_type;


-- ============================================
-- 12. PROCESSING PERFORMANCE STATS
-- ============================================
SELECT
    COUNT(*) as total_decisions,
    ROUND(AVG(processing_duration_seconds), 2) as avg_processing_time,
    MIN(processing_duration_seconds) as min_processing_time,
    MAX(processing_duration_seconds) as max_processing_time,
    ROUND(AVG(confidence_level), 2) as avg_confidence
FROM decisions;


-- ============================================
-- 13. DECISION CLASSIFICATION BREAKDOWN
-- ============================================
SELECT
    application_status,
    COUNT(*) as count,
    ROUND(AVG(confidence_level), 2) as avg_confidence,
    ROUND(AVG(risk_score), 2) as avg_risk_score
FROM decisions
GROUP BY application_status;


-- ============================================
-- 14. COUNT TOTAL RECORDS
-- ============================================
SELECT
    'applications' as table_name,
    COUNT(*) as total_records
FROM applications
UNION ALL
SELECT
    'decisions' as table_name,
    COUNT(*) as total_records
FROM decisions;


-- ============================================
-- 15. RECENTLY PROCESSED APPLICATIONS (LAST 10)
-- ============================================
SELECT
    applicant_id,
    applicant_name,
    status,
    risk_score,
    income,
    credit_score,
    created_at
FROM applications
ORDER BY created_at DESC
LIMIT 10;


-- ============================================
-- 16. INCOME VS LOAN AMOUNT ANALYSIS
-- ============================================
SELECT
    applicant_id,
    applicant_name,
    income,
    loan_amount,
    ROUND((loan_amount / income * 100), 2) as loan_to_income_ratio,
    status,
    created_at
FROM applications
ORDER BY (loan_amount / income) DESC;


-- ============================================
-- 17. DELETE ALL TEST DATA (USE WITH CAUTION)
-- ============================================
-- DELETE FROM decisions;
-- DELETE FROM applications;
-- SET FOREIGN_KEY_CHECKS=1;


-- ============================================
-- 18. VIEW DATABASE SIZE
-- ============================================
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_in_mb
FROM information_schema.TABLES
WHERE table_schema = 'loan_approval';


-- ============================================
-- 19. VIEW TABLE STRUCTURE
-- ============================================
DESCRIBE applications;
DESCRIBE decisions;
SHOW CREATE TABLE applications;
SHOW CREATE TABLE decisions;


-- ============================================
-- 20. APPLICATIONS WITH NO DECISIONS YET
-- ============================================
SELECT
    a.applicant_id,
    a.applicant_name,
    a.status,
    a.created_at
FROM applications a
LEFT JOIN decisions d ON a.applicant_id = d.applicant_id
WHERE d.applicant_id IS NULL;
