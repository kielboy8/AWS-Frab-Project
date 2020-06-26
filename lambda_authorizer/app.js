exports.handler = function (event, context, callback) {
  // console.log('headers: ', JSON.stringify(event.authorizationToken))
  let authorizationHeader = event.authorizationToken

  if (!authorizationHeader) return callback('Unauthorized')

  let encodedCreds = authorizationHeader.split(' ')[1]
  let plainCreds = (new Buffer(encodedCreds, 'base64')).toString().split(':')
  let username = plainCreds[0]
  let password = plainCreds[1]
  console.log('username', username)
  console.log('password', password)
  if (!(username === 'some-api-token' && password === '')) return callback('Unauthorized')

  var authResponse = buildAllowAllPolicy(event, username)

  callback(null, authResponse)
}

function buildAllowAllPolicy (event, principalId) {
  var apiOptions = {}
  var tmp = event.methodArn.split(':')
  var apiGatewayArnTmp = tmp[5].split('/')
  var awsAccountId = tmp[4]
  var awsRegion = tmp[3]
  var restApiId = apiGatewayArnTmp[0]
  var stage = apiGatewayArnTmp[1]
  var apiArn = 'arn:aws:execute-api:' + awsRegion + ':' + awsAccountId + ':' +
    restApiId + '/' + stage + '/*/*'
  const policy = {
    principalId: principalId,
    policyDocument: {
      Version: '2012-10-17',
      Statement: [
        {
          Action: 'execute-api:Invoke',
          Effect: 'Allow',
          Resource: [apiArn]
        }
      ]
    }
  }
  return policy
}