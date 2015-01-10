fab -u root -p harry4u hosts:beta,api,Y upstart:stop
fab -u root -p harry4u hosts:beta,worker,Y upstart:stop
fab -u root -p harry4u hosts:beta,singleton,Y upstart:stop
