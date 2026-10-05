'use strict';
// Parity with QRclima services/user-service.ts calculateProfileCompleteness.
// A regression test compares this contract with a synthetic complete/incomplete profile.
function profileCompleteness(profile) {
  const checks = [
    [!!profile.alias,5], [!!profile.city,5], [(profile.experienceYears || 0)>0,5],
    [!!profile.termsAcceptedAt,5], [!!profile.privacyAcceptedAt,5],
    [!!(profile.baseLat && profile.baseLng),5], [!!profile.signature,5],
    [!!profile.preferredNavigationApp,5], [!!profile.photoURL,5],
    [(profile.stats?.servicesCount || 0)>=1,13], [(profile.stats?.qrsActive || 0)>=1,8],
    [!!profile.achievements?.firstClient,8], [!!profile.achievements?.firstAgenda,8],
    [!!profile.achievements?.firstLabelsPdf,6],
    [(profile.stats?.sosParticipated || 0)>=1 || (profile.stats?.sosSolved || 0)>=1,6],
    [(profile.stats?.trainingCompleted || 0)>=1,6],
  ];
  return checks.reduce((sum,[met,weight])=>sum+(met?weight:0),0);
}
module.exports = {profileCompleteness};
